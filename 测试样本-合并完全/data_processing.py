from __future__ import annotations
import re, json
from pathlib import Path
from typing import List, Union, Optional
import pandas as pd
import io
from datetime import datetime, timedelta
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.styles import Alignment

# ———————————————— 1. 解析 + 标注 DataFrame ————————————————
def load_and_process(filepath: str, MAPPING_FILE,speaker_map) -> pd.DataFrame:
    # 读取 txt → list[str]
    
    df_nick = pd.read_excel(MAPPING_FILE, sheet_name="昵称映射")
    # 确保都是 str，并去两端空白
    df_nick["真实客服"] = df_nick["真实客服"].astype(str).str.strip()
    df_nick["昵称"]    = df_nick["昵称"].astype(str).str.strip()
    nickname_to_real = (
    df_nick
    .groupby("真实客服", sort=False)["昵称"]
    .apply(list)
    .to_dict()
    )

    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read().splitlines()
    recs, cur_grp, cur_obj = [], None, None
    pat = re.compile(r"(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2})\s+(.+)")
    i = 0
    while i < len(raw):
        line = raw[i].strip()
        if line.startswith("消息分组:"):
            cur_grp = line.split(":", 1)[1].strip(); i += 1; continue
        if line.startswith("消息对象:"):
            cur_obj = line.split(":", 1)[1].strip(); i += 1; continue
        m = pat.match(line)
        if m and cur_obj:
            t, sender = m.groups(); i += 1
            content = raw[i].strip() if i < len(raw) else ""
            recs.append({
                "消息分组": cur_grp,
                "聊天对象/群": cur_obj,
                "时间": t,
                "发言人": sender,
                "消息内容": content
            })
        i += 1
    df = pd.DataFrame(recs)
    df.drop_duplicates(inplace=True)
    df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
    # 标注 使用人 & 真实客服
    df['使用人'] = df['发言人']
    df['真实客服'] = None
    for real, nicks in nickname_to_real.items():
        pat = "|".join(re.escape(x) for x in nicks + [real])
        df.loc[df['使用人'].str.contains(pat, na=False), '真实客服'] = real 
    # 提取 speaker_id
    df['speaker_id'] = (
        df['发言人']
          .str.extract(r'\((\d+)\)')
          .fillna(df['发言人'])
    )
    # 去掉撤回消息 & 指定群
    df = df[~df['speaker_id'].isin(['10000', '1000000','系统消息(1000000)'])]
    df = df[~df['聊天对象/群'].isin(['青瓷客服打卡群'])]
    df["研发"] = df["speaker_id"].map(speaker_map)
    
    #数据清洗
    
    # 1. 处理“空行”或“[表情]”的情况
    mask_empty_or_emoji = df["消息内容"].astype(str).str.strip().isin(["", "[表情]"])
    # 2. 处理灌水词（可自行扩展）
    spam_words = ["+1", "冲", "蹲", "up", "哈", "嘿", "哦"]
    mask_spam = df["消息内容"].isin(spam_words)
    # 合并两个条件
    mask_to_drop = mask_empty_or_emoji | mask_spam
    # 删除这些无效行
    df_cleaned = df[~mask_to_drop].copy()
    
    return df_cleaned





# def load_and_process(filepath: str, nickname_to_real_path: str, speaker_map: dict) -> pd.DataFrame:
#     ...

def _identify_speaker(row) -> str:
    """判定说话者类型：研发ID / 客服ID / 玩家ID"""
    if pd.notna(row.get("研发")):
        return "研发ID"
    elif pd.notna(row.get("真实客服")):
        return "客服ID"
    else:
        return "玩家ID"

def _to_dt(x) -> pd.Timestamp:
    return pd.to_datetime(x, errors="coerce")

def build_jsonl_for_range(
    pathtxt: Union[str, Path],
    mapping_file: Union[str, Path],
    speaker_map: Optional[dict] = None,
    start_time: Optional[Union[str, datetime]] = None,
    end_time:   Optional[Union[str, datetime]] = None,
    return_str: bool = False,
) -> Union[List[str], str]:
    """解析 txt + 映射表 → JSONL；时间参数可为空表示全量"""
    df01 = load_and_process(str(pathtxt), str(mapping_file), speaker_map or {})
    if "时间" not in df01.columns:
        raise ValueError("df01 缺少列：时间")

    df01["时间"] = _to_dt(df01["时间"])

    # ✅ 可选时间过滤
    filtered = df01
    if start_time is not None:
        st = pd.to_datetime(start_time)
        filtered = filtered.loc[filtered["时间"] >= st]
    if end_time is not None:
        et = pd.to_datetime(end_time)
        filtered = filtered.loc[filtered["时间"] < et]

    # 取需要列并判定身份
    need_cols = ["时间", "发言人", "消息内容", "真实客服", "研发", "speaker_id"]
    for c in need_cols:
        if c not in filtered.columns:
            filtered[c] = pd.NA
    filtered["玩家/客服/研发"] = filtered.apply(_identify_speaker, axis=1)

    # 拆日期时分秒
    filtered["日期"] = filtered["时间"].dt.date.astype(str)
    filtered["时分秒"] = filtered["时间"].dt.time.astype(str)

    # 组装 JSONL
    jsonl_lines = []
    for _, row in filtered.iterrows():
        role = row["玩家/客服/研发"]
        speaker = str(row.get("发言人", ""))
        content = str(row.get("消息内容", "")).strip()
        obj = None
        if role == "玩家ID":
            obj = {"发言日期": row["日期"], "发言时间": row["时分秒"],
                   "玩家ID": speaker, "玩家消息": content}
        elif role == "客服ID":
            obj = {"发言日期": row["日期"], "发言时间": row["时分秒"],
                   "客服ID": speaker, "客服消息": content}
        elif role == "研发ID":
            obj = {"发言日期": row["日期"], "发言时间": row["时分秒"],
                   "研发ID": speaker, "研发消息": content}
        if obj:
            jsonl_lines.append(json.dumps(obj, ensure_ascii=False))

    return "\n".join(jsonl_lines) if return_str else jsonl_lines


def save_jsonl(lines_or_str: Union[List[str], str], out_path: Union[str, Path]) -> Path:
    """把 JSONL 列表或字符串保存到文件"""
    p = Path(out_path)
    if isinstance(lines_or_str, list):
        text = "\n".join(lines_or_str)
    else:
        text = lines_or_str
    p.write_text(text, encoding="utf-8")
    return p


