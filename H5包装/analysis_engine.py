"""
玩家社群发言分析引擎
整合自 model_classifyV1_Copy1_Copy1.py 和 data_processing.py
"""
from __future__ import annotations
import json
import time
import re
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
import requests


# ==================== 数据处理模块 ====================

def load_and_process(filepath: str, mapping_file: str, speaker_map: dict) -> pd.DataFrame:
    """加载并处理QQ群聊天记录txt文件"""
    df_nick = pd.read_excel(mapping_file, sheet_name="昵称映射")
    df_nick["真实客服"] = df_nick["真实客服"].astype(str).str.strip()
    df_nick["昵称"] = df_nick["昵称"].astype(str).str.strip()
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
            cur_grp = line.split(":", 1)[1].strip()
            i += 1
            continue
        if line.startswith("消息对象:"):
            cur_obj = line.split(":", 1)[1].strip()
            i += 1
            continue
        m = pat.match(line)
        if m and cur_obj:
            t, sender = m.groups()
            i += 1
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
    
    df['使用人'] = df['发言人']
    df['真实客服'] = None
    for real, nicks in nickname_to_real.items():
        pat_nick = "|".join(re.escape(x) for x in nicks + [real])
        df.loc[df['使用人'].str.contains(pat_nick, na=False), '真实客服'] = real
    
    df['speaker_id'] = (
        df['发言人']
        .str.extract(r'\((\d+)\)')
        .fillna(df['发言人'])
    )
    
    df = df[~df['speaker_id'].isin(['10000', '1000000', '系统消息(1000000)'])]
    df = df[~df['聊天对象/群'].isin(['青瓷客服打卡群'])]
    df["研发"] = df["speaker_id"].map(speaker_map)
    
    # 数据清洗
    mask_empty_or_emoji = df["消息内容"].astype(str).str.strip().isin(["", "[表情]"])
    spam_words = ["+1", "冲", "蹲", "up", "哈", "嘿", "哦"]
    mask_spam = df["消息内容"].isin(spam_words)
    mask_to_drop = mask_empty_or_emoji | mask_spam
    df_cleaned = df[~mask_to_drop].copy()
    
    return df_cleaned


def _identify_speaker(row) -> str:
    """判定说话者类型"""
    if pd.notna(row.get("研发")):
        return "研发ID"
    elif pd.notna(row.get("真实客服")):
        return "客服ID"
    else:
        return "玩家ID"


def build_jsonl_for_range(
    pathtxt: Union[str, Path],
    mapping_file: Union[str, Path],
    speaker_map: Optional[dict] = None,
    start_time: Union[str, datetime] = "1970-01-01 00:00:00",
    end_time: Union[str, datetime] = "2100-01-01 00:00:00",
    return_str: bool = False,
) -> Union[List[str], str]:
    """将聊天数据转换为JSONL格式"""
    df01 = load_and_process(str(pathtxt), str(mapping_file), speaker_map or {})
    if "时间" not in df01.columns:
        raise ValueError("df01 缺少列：时间")

    df01["时间"] = pd.to_datetime(df01["时间"], errors="coerce")
    st = pd.to_datetime(start_time)
    et = pd.to_datetime(end_time)
    mask = (df01["时间"] >= st) & (df01["时间"] < et)
    filtered = df01.loc[mask].copy()

    need_cols = ["时间", "发言人", "消息内容", "真实客服", "研发", "speaker_id"]
    for c in need_cols:
        if c not in filtered.columns:
            filtered[c] = pd.NA
    filtered["玩家/客服/研发"] = filtered.apply(_identify_speaker, axis=1)

    filtered["日期"] = filtered["时间"].dt.date.astype(str)
    filtered["时分秒"] = filtered["时间"].dt.time.astype(str)

    jsonl_lines: List[str] = []
    for _, row in filtered.iterrows():
        role = row["玩家/客服/研发"]
        dt_date = row["日期"]
        dt_time = row["时分秒"]
        speaker = str(row.get("发言人", ""))
        content = str(row.get("消息内容", "")).strip()

        if role == "玩家ID":
            obj = {"发言日期": dt_date, "发言时间": dt_time, "玩家ID": speaker, "玩家消息": content}
        elif role == "客服ID":
            obj = {"发言日期": dt_date, "发言时间": dt_time, "客服ID": speaker, "客服消息": content}
        elif role == "研发ID":
            obj = {"发言日期": dt_date, "发言时间": dt_time, "研发ID": speaker, "研发消息": content}
        else:
            continue

        jsonl_lines.append(json.dumps(obj, ensure_ascii=False))

    return "\n".join(jsonl_lines) if return_str else jsonl_lines


# ==================== 模型调用模块 ====================

def load_system_prompt(path: Path) -> str:
    """加载系统提示词"""
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def build_user_prompt_filter(json_lines: List[str]) -> str:
    """构建模型#1的用户提示（筛选游戏相关发言）"""
    return (
        "以下是若干玩家/客服/研发的发言记录，请根据系统提示中规则，"
        "判断哪些是【与游戏内容相关】的发言，保留这些 JSON 行，不相关的忽略。"
        "请仅输出【相关发言的原始 JSON 行】，严格保持格式不变。\n\n"
        "【输入】：\n" + "\n".join(json_lines)
    )


def build_user_prompt_cluster(jsonl_block: str) -> str:
    """构建模型#2的用户提示（话题簇划分）"""
    return (
        "以下是输入数据（JSONL 格式，每行一个发言对象）：\n\n"
        "请先完整阅读全部输入，然后按系统提示中的话题簇规则进行划分。\n"
        "【输出要求】只输出若干 JSON 对象，每个话题簇一个 JSON；"
        "禁止使用 ```json 或 ``` 等 Markdown 代码块，禁止输出解释文字。\n\n"
        "【输入】：\n" + jsonl_block
    )


def build_user_prompt_cluster_agg(jsonl_block: str) -> str:
    """构建模型#3的用户提示（话题簇聚合）"""
    return (
        "以下是输入数据（JSONL 格式，每行一个发言对象）：\n\n"
        "请先完整阅读全部输入，然后按系统提示中的话题簇规则进行划分。\n"
        "【输出要求】只输出若干 JSON 对象，每个话题簇一个 JSON；"
        "禁止使用 ```json 或 ``` 等 Markdown 代码块，禁止输出解释文字。\n\n"
        "【输入】：\n" + jsonl_block
    )


def build_user_prompt_subcluster_opinion(
    topic_id: str,
    discussion_point: str,
    dialogs: List[Dict[str, Any]],
) -> str:
    """构建模型#4的用户提示（玩家观点分析）"""
    header_line = json.dumps({"话题簇ID": topic_id, "讨论点": discussion_point}, ensure_ascii=False)
    dialog_lines = "\n".join(json.dumps(d, ensure_ascii=False) for d in dialogs)
    jsonl_block = header_line + "\n" + dialog_lines

    return (
        "禁止使用 ```json 或 ``` 等 Markdown 代码块，禁止输出解释文字。\n\n"
        "【输入】本次所有数据（JSONL，第一行为话题簇信息，其余为发言）：\n"
        + jsonl_block
    )


def call_ark_chat_completions(
    api_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 32700,
    timeout: int = 600,
    retries: int = 2,
) -> str:
    """调用火山方舟API"""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Ark API 调用失败: {last_err}")


# ==================== 辅助函数 ====================

def infer_date_for_batch(cluster_json_list: List[Dict], batch_lines: List[str]) -> str:
    """从数据中推断日期"""
    for obj in cluster_json_list:
        title = str(obj.get("话题簇") or obj.get("聚合话题簇") or "")
        m = re.search(r"(\d{4}-\d{2}-\d{2})", title)
        if m:
            return m.group(1)

    for line in batch_lines:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        date_str = msg.get("发言日期") or msg.get("日期")
        if date_str:
            return date_str

    raise ValueError("无法推断日期")


def assign_global_cluster_ids(cluster_list: List[Dict], date_str: str, batch_id: str) -> List[Dict]:
    """为话题簇分配全局唯一ID"""
    for idx, cluster in enumerate(cluster_list, start=1):
        cluster["_cluster_id"] = f"{date_str}_{batch_id}_{idx:02d}"
    return cluster_list


def aggregate_cluster_outputs(batch_outputs: List[str]) -> str:
    """聚合多批次的话题簇输出"""
    all_lines = []
    for text in batch_outputs:
        if not text:
            continue
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                clean_line = json.dumps(obj, ensure_ascii=False)
                all_lines.append(clean_line)
            except Exception:
                continue
    return "\n".join(all_lines)


def _parse_time_ranges(time_axis_str: str) -> List[Tuple[datetime, datetime]]:
    """解析时间轴字符串"""
    if not time_axis_str or not isinstance(time_axis_str, str):
        return []

    s = time_axis_str.strip()
    for sep in ["至", "到", "~", "～", "—", "–"]:
        s = s.replace(sep, "-")
    s = s.replace(" ", "")

    parts = [p.strip() for p in s.split("、") if p.strip()]
    ranges = []

    for p in parts:
        if "-" not in p:
            continue
        a, b = [x.strip() for x in p.split("-", 1)]
        try:
            start_t = datetime.strptime(a, "%H:%M:%S").time()
            end_t = datetime.strptime(b, "%H:%M:%S").time()
            ranges.append((start_t, end_t))
        except Exception:
            continue

    return ranges


def match_dialogs_by_time(
    messages: List[Dict[str, Any]],
    date_str: str,
    time_axis_str: Optional[str],
    dedup: bool = True,
) -> List[Dict[str, Any]]:
    """根据时间轴匹配对话"""
    if not messages or not date_str:
        return []
    if not time_axis_str:
        return []

    ranges = _parse_time_ranges(time_axis_str)
    if not ranges:
        return []

    matched = []
    seen = set()

    for row in messages:
        if (row.get("发言日期") or "") != date_str:
            continue

        ts = row.get("发言时间") or ""
        try:
            t = datetime.strptime(ts, "%H:%M:%S").time()
        except Exception:
            continue

        hit = False
        for start_t, end_t in ranges:
            if start_t <= end_t:
                if start_t <= t <= end_t:
                    hit = True
                    break
            else:
                if t >= start_t or t <= end_t:
                    hit = True
                    break

        if not hit:
            continue

        if dedup:
            key = (
                row.get("_idx"),
                row.get("发言日期"),
                row.get("发言时间"),
                row.get("玩家ID"),
                row.get("玩家消息"),
            )
            if key in seen:
                continue
            seen.add(key)

        matched.append(row)

    return matched


def compute_heat_score(U: int, M: int) -> float:
    """计算热度评分"""
    if U == 0 or M == 0:
        return 0.0
    return round(U * math.sqrt(M), 2)


def extract_top5_heat_clusters(
    cluster_list: List[Dict],
    raw_lines: List[str],
    top_k: int = 5
) -> List[Dict]:
    """提取热度Top5话题簇"""
    parsed_msgs = [json.loads(line.strip()) for line in raw_lines if line.strip()]
    enriched = []

    for cluster in cluster_list:
        date = cluster.get("日期")
        time_axis = cluster.get("时间轴")
        matched = match_dialogs_by_time(parsed_msgs, date, time_axis)

        players = {msg.get("玩家ID") for msg in matched if msg.get("玩家ID")}
        U = len(players)
        M = len(matched)
        heat = compute_heat_score(U, M)

        enriched.append({
            "聚合话题簇": cluster.get("话题簇") or cluster.get("聚合话题簇") or "未知",
            "子话题簇列表": cluster.get("子话题簇列表", []),
            "日期": date,
            "时间轴": time_axis,
            "发言玩家总数": U,
            "发言总数": M,
            "热度评分": heat
        })

    enriched.sort(key=lambda x: x["热度评分"], reverse=True)
    return enriched[:top_k]


def extract_time_axis_from_title(title: str) -> str:
    """从话题簇标题中提取时间轴"""
    if not title:
        return ""
    m = re.search(r"(\d{2}:\d{2}:\d{2})\s*[-至到~～—–]\s*(\d{2}:\d{2}:\d{2})", title)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return ""


def parse_jsonl_text(text: str) -> List[Dict[str, Any]]:
    """解析JSONL文本"""
    if not text:
        return []

    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\s*", "", s)
        s = re.sub(r"\s*```$", "", s)

    results = []
    for raw in s.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].lstrip()
        if not line.startswith("{"):
            continue
        if line.endswith(","):
            line = line[:-1].rstrip()

        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                results.append(obj)
        except json.JSONDecodeError:
            continue

    return results


def ensure_time_axis_key(c: Dict[str, Any]) -> bool:
    """确保字典中有时间轴字段"""
    ta = c.get("时间轴")
    if isinstance(ta, str) and ta.strip():
        return False

    for k in list(c.keys()):
        if "时间" in str(k) and k != "时间轴":
            v = c.get(k)
            if isinstance(v, str) and v.strip():
                c["时间轴"] = v.strip()
                return True
    return False


def ensure_subcluster_list_key(c: Dict[str, Any]) -> bool:
    """确保字典中有子话题簇列表字段"""
    if isinstance(c.get("子话题簇列表"), list) and c["子话题簇列表"]:
        return False

    candidates = ["子话题簇列表", "子话提簇列表", "子话题簇ID列表", "子簇列表", "子话题簇"]
    for k in candidates:
        v = c.get(k)
        if v is None:
            continue
        if isinstance(v, list):
            c["子话题簇列表"] = v
            return True
        if isinstance(v, str) and v.strip():
            c["子话题簇列表"] = [x.strip() for x in v.split("、") if x.strip()]
            return True
    return False


def parse_and_normalize_opinion_output(
    opinion_output: str,
    topic_id: str,
    discussion_point: str,
) -> Optional[Dict[str, Any]]:
    """解析并标准化模型#4的输出"""
    if not opinion_output:
        return None

    s = opinion_output.strip()
    
    # 尝试直接解析
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # 尝试逐行解析
    for line in s.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue

    return None


def build_daily_top5_opinion_records(
    top5_results: List[Dict],
    sub_opinion_map: Dict[str, Dict],
) -> List[Dict]:
    """构建带观点的Top5结果"""
    final_results = []
    
    for cluster in top5_results:
        cid_list = cluster.get("子话题簇列表", [])
        discussion_list = []
        
        for idx, cid in enumerate(cid_list, start=1):
            opinion = sub_opinion_map.get(cid)
            if not opinion:
                continue
            
            discussion_list.append({
                f"讨论点{idx}": opinion.get("讨论点", ""),
                "玩家观点": opinion.get("玩家观点", []),
                "代表性玩家发言示例": opinion.get("代表性玩家发言示例", [])
            })
        
        result = {
            "聚合话题簇": cluster.get("聚合话题簇"),
            "日期": cluster.get("日期"),
            "时间轴": cluster.get("时间轴"),
            "发言玩家总数": cluster.get("发言玩家总数"),
            "发言总数": cluster.get("发言总数"),
            "热度评分": cluster.get("热度评分"),
            "讨论点列表": discussion_list
        }
        final_results.append(result)
    
    return final_results


# ==================== 主分析类 ====================

class PlayerCommunityAnalyzer:
    """玩家社群发言分析器"""
    
    def __init__(
        self,
        api_url: str,
        api_key: str,
        v3_model_id: str,
        v3_1_model_id: str,
        prompt_dir: Path,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.v3_model_id = v3_model_id
        self.v3_1_model_id = v3_1_model_id
        self.prompt_dir = Path(prompt_dir)
        
        # 加载提示词
        self.system_prompt01 = load_system_prompt(self.prompt_dir / "提示词1.md")
        self.system_prompt02 = load_system_prompt(self.prompt_dir / "2话题分类.md")
        self.system_prompt03 = load_system_prompt(self.prompt_dir / "3日聚合.md")
        self.system_prompt04 = load_system_prompt(self.prompt_dir / "2话题分类和总结.md")
    
    def analyze(
        self,
        txt_path: str,
        mapping_file: str,
        speaker_map: Dict[str, str],
        start_time: str = None,
        end_time: str = None,
        target_date: str = None,  # 保持向后兼容
        batch_size: int = 300,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """
        执行完整的分析流程
        
        Args:
            txt_path: QQ群聊天记录txt文件路径
            mapping_file: 客服昵称映射Excel文件路径
            speaker_map: 研发人员ID映射
            start_time: 开始时间，格式：YYYY-MM-DD HH:MM:SS（与 top5_Q1.ipynb 一致）
            end_time: 结束时间，格式：YYYY-MM-DD HH:MM:SS（与 top5_Q1.ipynb 一致）
            target_date: [已废弃] 目标分析日期，格式：YYYY-MM-DD（保持向后兼容）
            batch_size: 每批处理的消息数量
            progress_callback: 进度回调函数，接收 (current_step, total_steps, message) 参数
        
        Returns:
            包含分析结果的字典
        """
        # 处理时间参数：优先使用 start_time/end_time，其次使用 target_date
        if start_time and end_time:
            # 从 start_time 提取日期用于显示
            display_date = start_time.split(" ")[0] if " " in start_time else start_time[:10]
        elif target_date:
            # 向后兼容：使用 target_date 生成时间范围
            start_time = f"{target_date} 00:00:00"
            end_time_dt = datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)
            end_time = end_time_dt.strftime("%Y-%m-%d %H:%M:%S")
            display_date = target_date
        else:
            raise ValueError("必须提供 start_time/end_time 或 target_date 参数")
        
        results = {
            "date": display_date,
            "time_range": f"{start_time} ~ {end_time}",
            "total_messages": 0,
            "filtered_messages": 0,
            "top5_clusters": [],
            "status": "processing",
            "error": None,
        }
        
        try:
            # Step 1: 数据预处理
            if progress_callback:
                progress_callback(1, 6, f"正在加载数据 [{start_time} ~ {end_time}]...")
            
            jsonl_lines = build_jsonl_for_range(
                pathtxt=txt_path,
                mapping_file=mapping_file,
                speaker_map=speaker_map,
                start_time=start_time,
                end_time=end_time,
                return_str=False,
            )
            
            results["total_messages"] = len(jsonl_lines)
            
            if len(jsonl_lines) == 0:
                results["status"] = "no_data"
                results["error"] = "指定日期没有聊天记录"
                return results
            
            # Step 2: 分批处理 - 模型#1筛选 + 模型#2话题簇划分
            if progress_callback:
                progress_callback(2, 6, "正在进行游戏相关发言筛选和话题簇划分...")
            
            total_batches = (len(jsonl_lines) + batch_size - 1) // batch_size
            batch_cluster_outputs = []
            total_filtered = 0
            
            for b in range(total_batches):
                start_idx = b * batch_size
                end_idx = min(start_idx + batch_size, len(jsonl_lines))
                batch_lines = jsonl_lines[start_idx:end_idx]
                
                # 模型#1：筛选游戏相关发言
                user_prompt1 = build_user_prompt_filter(batch_lines)
                output_filter = call_ark_chat_completions(
                    api_url=self.api_url,
                    api_key=self.api_key,
                    model=self.v3_model_id,
                    system_prompt=self.system_prompt01,
                    user_prompt=user_prompt1,
                    temperature=0.2,
                    max_tokens=16384,
                    timeout=600,
                    retries=2,
                )
                
                if not output_filter:
                    continue
                
                filter_count = sum(1 for line in output_filter.splitlines() if line.strip())
                total_filtered += filter_count
                
                # 模型#2：话题簇划分
                user_prompt2 = build_user_prompt_cluster(output_filter)
                output_cluster = call_ark_chat_completions(
                    api_url=self.api_url,
                    api_key=self.api_key,
                    model=self.v3_1_model_id,
                    system_prompt=self.system_prompt02,
                    user_prompt=user_prompt2,
                    temperature=0.2,
                    max_tokens=16384,
                    timeout=600,
                    retries=2,
                )
                
                if not output_cluster:
                    continue
                
                # 解析并添加cluster_id
                try:
                    cluster_json_list = []
                    for line in output_cluster.strip().splitlines():
                        line = line.strip()
                        if not line.startswith("{"):
                            continue
                        obj = json.loads(line)
                        for key in list(obj.keys()):
                            if key.startswith("话题簇") and key != "话题簇":
                                obj["话题簇"] = obj.pop(key)
                        cluster_json_list.append(obj)
                    
                    date_str = infer_date_for_batch(cluster_json_list, batch_lines)
                    batch_id = f"B{b+1}"
                    cluster_json_list = assign_global_cluster_ids(cluster_json_list, date_str, batch_id)
                    
                    output_cluster_with_ids = "\n".join(json.dumps(c, ensure_ascii=False) for c in cluster_json_list)
                    batch_cluster_outputs.append(output_cluster_with_ids)
                except Exception:
                    continue
                
                time.sleep(1)  # 防止QPS限流
            
            results["filtered_messages"] = total_filtered
            
            # Step 3: 话题簇聚合
            if progress_callback:
                progress_callback(3, 6, "正在聚合话题簇...")
            
            all_cluster = aggregate_cluster_outputs(batch_cluster_outputs)
            
            user_prompt3 = build_user_prompt_cluster_agg(all_cluster)
            output_cluster_agg = call_ark_chat_completions(
                api_url=self.api_url,
                api_key=self.api_key,
                model=self.v3_1_model_id,
                system_prompt=self.system_prompt03,
                user_prompt=user_prompt3,
                temperature=0.2,
                max_tokens=16384,
                timeout=600,
                retries=2,
            )
            
            # Step 4: 计算热度Top5
            if progress_callback:
                progress_callback(4, 6, "正在计算热度Top5...")
            
            parsed_subclusters = parse_jsonl_text(all_cluster)
            parsed_clusters = parse_jsonl_text(output_cluster_agg)
            
            for c in parsed_clusters:
                ensure_time_axis_key(c)
                ensure_subcluster_list_key(c)
            
            top5_results = extract_top5_heat_clusters(parsed_clusters, jsonl_lines, top_k=5)
            
            # Step 5: 玩家观点分析
            if progress_callback:
                progress_callback(5, 6, "正在分析玩家观点...")
            
            sub_map = {row.get("_cluster_id"): row for row in parsed_subclusters if row.get("_cluster_id")}
            sub_opinion_map = {}
            parsed_msgs = [json.loads(line.strip()) for line in jsonl_lines if line.strip()]
            
            for cluster in top5_results:
                date = cluster["日期"]
                cid_list = cluster.get("子话题簇列表", [])
                
                for cid in cid_list:
                    sub = sub_map.get(cid)
                    if not sub:
                        continue
                    
                    sub_title = sub.get("话题簇", "") or ""
                    sub_time_axis = extract_time_axis_from_title(sub_title)
                    dialogs = match_dialogs_by_time(parsed_msgs, date, sub_time_axis)
                    
                    discussion_point = sub.get("核心对象/机制") or sub.get("话题簇") or ""
                    topic_id = sub.get("_cluster_id", cid)
                    
                    if not dialogs:
                        continue
                    
                    user_prompt4 = build_user_prompt_subcluster_opinion(
                        topic_id=topic_id,
                        discussion_point=discussion_point,
                        dialogs=dialogs,
                    )
                    
                    opinion_output = call_ark_chat_completions(
                        api_url=self.api_url,
                        api_key=self.api_key,
                        model=self.v3_1_model_id,
                        system_prompt=self.system_prompt04,
                        user_prompt=user_prompt4,
                        temperature=0.2,
                        max_tokens=16384,
                        timeout=600,
                        retries=2,
                    )
                    
                    opinion_obj = parse_and_normalize_opinion_output(
                        opinion_output=opinion_output,
                        topic_id=topic_id,
                        discussion_point=discussion_point,
                    )
                    
                    if opinion_obj:
                        sub_opinion_map[topic_id] = opinion_obj
            
            # Step 6: 组装最终结果
            if progress_callback:
                progress_callback(6, 6, "正在生成最终报告...")
            
            final_top5 = build_daily_top5_opinion_records(top5_results, sub_opinion_map)
            
            results["top5_clusters"] = final_top5
            results["status"] = "success"
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results

