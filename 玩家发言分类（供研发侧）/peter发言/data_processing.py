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
# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from typing import List, Optional, Union

# 头部行：日期 时间 发言人(qq)
# 例：2025-07-02 18:19:00 Peter本尊(16186514)
HEADER_RE = re.compile(
    r"^(?P<date>\d{2,4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<sender>.+?)\s*$"
)

def _read_text_auto(pathtxt: str) -> str:
    """尽量自动处理 QQ 导出的编码（utf-8/utf-8-sig/gb18030）"""
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            with open(pathtxt, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except Exception:
            pass
    # 最后兜底：容错读取
    with open(pathtxt, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _normalize_date(date_str: str) -> str:
    """
    把 '025-07-02' / '25-07-02' 之类归一成 '2025-07-02'
    规则：
      - 4位年：原样
      - 3位年：前面补 '2' => 025 -> 2025
      - 2位年：前面补 '20' => 25 -> 2025
    """
    parts = date_str.split("-")
    if len(parts) != 3:
        return date_str
    y, m, d = parts
    if len(y) == 4:
        return f"{y}-{m}-{d}"
    if len(y) == 3:
        return f"2{y}-{m}-{d}"
    if len(y) == 2:
        return f"20{y}-{m}-{d}"
    return date_str

def _to_dt(x: Optional[Union[str, datetime]]) -> Optional[datetime]:
    if x is None:
        return None
    if isinstance(x, datetime):
        return x
    x = str(x).strip()
    # 支持：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(x, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间：{x}（请用 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:MM:SS'）")

def build_jsonl_for_range(
    pathtxt: str,
    start: Optional[Union[str, datetime]] = None,
    end: Optional[Union[str, datetime]] = None,
    return_str: bool = False,   # False -> list[str]；True -> 单个 jsonl 字符串
) -> Union[List[str], str]:
    """
    将 QQ txt 导出转为 jsonl。
    解析规则：
      - 遇到“日期 时间 发言人”行 => 新消息块开始
      - 消息内容为后续多行，直到下一条 header 或文件结束
      - 会跳过纯空消息块
      - 可用 start/end 过滤（闭区间 start <= t <= end）
    输出字段（与你现在的下游一致）：
      发言日期、发言时间、玩家ID、玩家消息
    """
    text = _read_text_auto(pathtxt)
    lines = text.splitlines()

    start_dt = _to_dt(start)
    end_dt = _to_dt(end)

    out_lines: List[str] = []

    cur_date = None
    cur_time = None
    cur_sender = None
    cur_msg_lines: List[str] = []

    def flush_current():
        nonlocal cur_date, cur_time, cur_sender, cur_msg_lines, out_lines
        if not (cur_date and cur_time and cur_sender):
            return
        msg = "\n".join([s.rstrip() for s in cur_msg_lines]).strip()
        if not msg:
            return

        dt_str = f"{cur_date} {cur_time}"
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 极端兜底：不解析时间就不做过滤
            dt = None

        if dt is not None:
            if start_dt and dt < start_dt:
                return
            if end_dt and dt > end_dt:
                return

        obj = {
            "发言日期": cur_date,
            "发言时间": cur_time,
            "玩家ID": cur_sender,
            "玩家消息": msg,
        }
        out_lines.append(json.dumps(obj, ensure_ascii=False))

    for raw in lines:
        line = raw.rstrip("\n")
        m = HEADER_RE.match(line.strip())
        if m:
            # 新 header：先落盘上一条
            flush_current()
            cur_msg_lines = []
            cur_date = _normalize_date(m.group("date").strip())
            cur_time = m.group("time").strip()
            cur_sender = m.group("sender").strip()
        else:
            # 非 header：属于消息正文（保留空行也行；这里保留但最终 strip 会清理）
            if cur_date is not None:
                cur_msg_lines.append(line)

    # 文件末尾最后一条
    flush_current()

    if return_str:
        return "\n".join(out_lines)
    return out_lines



