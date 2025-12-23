# -*- coding: utf-8 -*-
"""
只提取 QQ 群聊 txt 中 Peter 本尊(16186514) 的发言，输出为新 txt。

适配格式：
YYYY-MM-DD HH:MM:SS 昵称(ID)
<消息内容(可多行)>
（直到下一条时间戳行出现）
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


# ======== 你只需要改这里的路径/ID ========
INPUT_TXT = r"E:\项目\玩家社群分析智能体\玩家发言分类（供研发侧）\1215《欢迎来到地球》测试2群.txt"
OUTPUT_TXT = r"E:\项目\玩家社群分析智能体\玩家发言分类（供研发侧）\Peter发言_测试2群PURE.txt"

PETER_ID = "16186514"       # 以ID为准最稳
PETER_NAME_KW = "Peter本尊"  # 可留空字符串 ""，仅做兜底匹配
# ======================================


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
    raw_block: str


def try_read_text(path: str) -> str:
    # 常见：utf-8 / utf-8-sig / gb18030（兼容gbk）
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            with open(path, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # 兜底容错读
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_blocks(text: str) -> List[MsgBlock]:
    lines = text.splitlines()
    blocks: List[MsgBlock] = []

    cur_header: Optional[str] = None
    cur_dt: Optional[datetime] = None
    cur_sender_raw: Optional[str] = None
    cur_sender_id: Optional[str] = None
    cur_body: List[str] = []

    def flush():
        nonlocal cur_header, cur_dt, cur_sender_raw, cur_sender_id, cur_body
        if cur_header and cur_dt and cur_sender_raw is not None:
            raw = cur_header + "\n"
            if cur_body:
                raw += "\n".join(cur_body).rstrip("\n") + "\n"
            raw += "\n"  # 块间空行
            blocks.append(
                MsgBlock(
                    idx=len(blocks),
                    dt=cur_dt,
                    sender_raw=cur_sender_raw,
                    sender_id=cur_sender_id,
                    raw_block=raw,
                )
            )
        cur_header = None
        cur_dt = None
        cur_sender_raw = None
        cur_sender_id = None
        cur_body = []

    for line in lines:
        m = HEADER_RE.match(line.strip())
        if m:
            flush()
            cur_header = line.rstrip("\n")
            d = m.group("date")
            t = m.group("time")
            cur_dt = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M:%S")
            cur_sender_raw = m.group("sender").strip()

            mid = ID_RE.search(cur_sender_raw)
            cur_sender_id = mid.group(1) if mid else None
        else:
            # header之后的内容都算body；header之前的文件头信息会被自然忽略
            if cur_header is not None:
                cur_body.append(line.rstrip("\n"))

    flush()
    return blocks


def is_peter(b: MsgBlock, peter_id: str, peter_name_kw: str) -> bool:
    # 以 ID 匹配为主；名字关键词为兜底
    if b.sender_id == peter_id:
        return True
    if peter_name_kw and (peter_name_kw in (b.sender_raw or "")):
        return True
    return False


def main():
    text = try_read_text(INPUT_TXT)
    blocks = parse_blocks(text)

    kept = [b for b in blocks if is_peter(b, PETER_ID, PETER_NAME_KW)]

    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for b in kept:
            f.write(b.raw_block)

    print(f"总块数: {len(blocks)}")
    print(f"Peter块数: {len(kept)}")
    print(f"输出完成: {OUTPUT_TXT}")


if __name__ == "__main__":
    main()
