# -*- coding: utf-8 -*-
"""
从QQ群聊txt中提取：
- Peter本尊(16186514) 的发言
- 以及每条 Peter 发言上下 N 秒（默认60秒）内的相关玩家发言
输出为新的 txt（保留原始块格式）。
"""

import re
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


HEADER_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{1,2}:\d{2}:\d{2})\s+(?P<sender>.+?)\s*$"
)
ID_RE = re.compile(r"\((\d+)\)\s*$")


@dataclass
class MsgBlock:
    idx: int
    dt: datetime
    sender_raw: str
    sender_id: Optional[str]
    is_system: bool
    raw_block: str


def try_read_text(path: str) -> str:
    # 常见：utf-8 / utf-8-sig / gb18030（兼容gbk）
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            with open(path, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # 最后兜底：容错读
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_blocks(text: str) -> List[MsgBlock]:
    lines = text.splitlines()
    blocks: List[MsgBlock] = []

    cur_header_line: Optional[str] = None
    cur_header_match: Optional[re.Match] = None
    cur_body_lines: List[str] = []
    cur_dt: Optional[datetime] = None
    cur_sender_raw: Optional[str] = None
    cur_sender_id: Optional[str] = None
    cur_is_system: bool = False

    def flush():
        nonlocal cur_header_line, cur_header_match, cur_body_lines, cur_dt, cur_sender_raw, cur_sender_id, cur_is_system
        if cur_header_line and cur_dt and cur_sender_raw is not None:
            # 保留“头 + body原样”
            raw = cur_header_line + "\n"
            if cur_body_lines:
                raw += "\n".join(cur_body_lines).rstrip("\n") + "\n"
            raw += "\n"  # 块间空行
            blocks.append(
                MsgBlock(
                    idx=len(blocks),
                    dt=cur_dt,
                    sender_raw=cur_sender_raw,
                    sender_id=cur_sender_id,
                    is_system=cur_is_system,
                    raw_block=raw,
                )
            )
        cur_header_line = None
        cur_header_match = None
        cur_body_lines = []
        cur_dt = None
        cur_sender_raw = None
        cur_sender_id = None
        cur_is_system = False

    for line in lines:
        m = HEADER_RE.match(line.strip())
        if m:
            # 新块开始：先flush旧块
            flush()
            cur_header_line = line.rstrip("\n")
            cur_header_match = m
            d = m.group("date")
            t = m.group("time")
            cur_dt = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M:%S")
            cur_sender_raw = m.group("sender").strip()

            # sender_id（如果有）
            mid = ID_RE.search(cur_sender_raw)
            cur_sender_id = mid.group(1) if mid else None

            # 系统消息判定（你样例里是“系统消息(1000000)”）
            cur_is_system = ("系统消息" in cur_sender_raw) or (cur_sender_id == "1000000")
        else:
            # header之后的内容都算body（允许空行）
            if cur_header_line is not None:
                cur_body_lines.append(line.rstrip("\n"))
            # header之前的文件头信息忽略（如“消息分组…”）
    flush()
    return blocks


def is_peter(block: MsgBlock, peter_id: str, peter_name_kw: Optional[str]) -> bool:
    if block.sender_id == peter_id:
        return True
    if peter_name_kw and peter_name_kw in (block.sender_raw or ""):
        return True
    return False


def extract_context_blocks(
    blocks: List[MsgBlock],
    peter_id: str = "16186514",
    peter_name_kw: str = "Peter本尊",
    window_sec: int = 60,
    include_system: bool = False,
) -> List[MsgBlock]:
    # 1) 找到所有 Peter 发言时间点
    peter_times: List[datetime] = []
    for b in blocks:
        if is_peter(b, peter_id, peter_name_kw):
            peter_times.append(b.dt)

    if not peter_times:
        return []

    # 2) 合并时间窗口（避免多条Peter发言窗口重叠时重复计算）
    win = timedelta(seconds=window_sec)
    intervals: List[Tuple[datetime, datetime]] = []
    for t in sorted(peter_times):
        intervals.append((t - win, t + win))

    merged: List[Tuple[datetime, datetime]] = []
    for s, e in intervals:
        if not merged or s > merged[-1][1]:
            merged.append((s, e))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))

    # 3) 按原顺序挑出在任何窗口内的块：
    #    - Peter块必留
    #    - 玩家块：在窗口内
    #    - 系统消息：默认不留（可选）
    keep = []
    keep_idx = set()

    def in_any_interval(dt: datetime) -> bool:
        # merged 已排序
        for s, e in merged:
            if s <= dt <= e:
                return True
            if dt < s:
                return False
        return False

    for b in blocks:
        if is_peter(b, peter_id, peter_name_kw):
            if b.idx not in keep_idx:
                keep.append(b); keep_idx.add(b.idx)
            continue

        if not include_system and b.is_system:
            continue

        if in_any_interval(b.dt):
            if b.idx not in keep_idx:
                keep.append(b); keep_idx.add(b.idx)

    # 保持原始顺序
    keep.sort(key=lambda x: x.idx)
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input_txt",
        default=r"E:\项目\玩家社群分析智能体\玩家发言分类（供研发侧）\1215《欢迎来到地球》测试2群.txt",
        help="原始群聊txt路径"
    )
    ap.add_argument(
        "--output_txt",
        default=r"E:\项目\玩家社群分析智能体\玩家发言分类（供研发侧）\Peter发言总结_测试2群.txt",
        help="输出txt路径"
    )
    ap.add_argument("--peter_id", default="16186514")
    ap.add_argument("--peter_name_kw", default="Peter本尊")
    ap.add_argument("--window_sec", type=int, default=60)
    ap.add_argument("--include_system", action="store_true")
    args = ap.parse_args()


    text = try_read_text(args.input_txt)
    blocks = parse_blocks(text)
    kept = extract_context_blocks(
        blocks,
        peter_id=args.peter_id,
        peter_name_kw=args.peter_name_kw,
        window_sec=args.window_sec,
        include_system=args.include_system,
    )

    with open(args.output_txt, "w", encoding="utf-8") as f:
        for b in kept:
            f.write(b.raw_block)

    print(f"总块数: {len(blocks)}")
    print(f"保留块数: {len(kept)}")
    print(f"输出完成: {args.output_txt}")


if __name__ == "__main__":
    main()
