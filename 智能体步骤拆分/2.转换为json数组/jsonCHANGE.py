# jsonl_fix_and_export.py
# 读取 JSONL -> 标准化键名/空值 -> 成对裁剪空字段 -> 写出 out/fixed.json

from pathlib import Path
from collections import OrderedDict
import json, re, sys

# ======== 配置 =========
INPUT = Path(r"E:\项目\玩家社群分析智能体\2.转换为json数组\sample100 - 副本.jsonl")

WRAP_MODE = "array"   # "array" 输出 [ {...}, ... ] ; "object" 输出 {"data":[...]}
REPLACE_NULL = True   # True: :null -> :""
KEY_NORMALIZE = {
    # —— 玩家ID/客服ID ——（含标点与旧称）
    "玩家ID，": "玩家ID", "玩家ID,": "玩家ID", "玩家ID：": "玩家ID", "玩家ID:": "玩家ID",
    "玩家Id": "玩家ID", "玩家": "玩家ID", "发言人": "玩家ID",
    "客服ID，": "客服ID", "客服ID,": "客服ID", "客服ID：": "客服ID", "客服ID:": "客服ID",
    "真实客服": "客服ID", "客服": "客服ID",
    # —— 玩家消息/客服消息 ——（含标点）
    "玩家消息，": "玩家消息", "玩家消息,": "玩家消息", "玩家消息：": "玩家消息", "玩家消息:": "玩家消息",
    "客服消息，": "客服消息", "客服消息,": "客服消息", "客服消息：": "客服消息", "客服消息:": "客服消息",
    # —— 时间 ——（容错）
    "时间：": "时间", "时间:": "时间",
}
# 固定输出键顺序（先按此顺序放入；后续会按需“成对裁剪”空字段）
KEEP_KEYS_ORDER = ["时间", "玩家ID", "玩家消息", "客服ID", "客服消息"]

# ======== 输出目录（脚本同级/out）========
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
OUT_DIR = BASE_DIR / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize_commas(s: str) -> str:
    return s.replace("：", ":").replace("，", ",")

def fix_trailing_punct_keys(line: str) -> str:
    for bad, good in KEY_NORMALIZE.items():
        line = line.replace(f"\"{bad}\"", f"\"{good}\"")
    return line

def prune_empty_role_fields(obj: OrderedDict) -> OrderedDict:
    """若（玩家ID,玩家消息）同时为空，则删除这两键；若（客服ID,客服消息）同时为空，也删除这两键。"""
    def is_empty(v): return v is None or (isinstance(v, str) and v == "")
    # 玩家对
    if is_empty(obj.get("玩家ID")) and is_empty(obj.get("玩家消息")):
        obj.pop("玩家ID", None)
        obj.pop("玩家消息", None)
    # 客服对
    if is_empty(obj.get("客服ID")) and is_empty(obj.get("客服消息")):
        obj.pop("客服ID", None)
        obj.pop("客服消息", None)
    return obj

def parse_jsonl(path: Path):
    items, bad = [], 0
    with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        for idx, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            if not line.startswith("{") or line.endswith("..."):
                bad += 1
                continue

            line = normalize_commas(line)
            line = fix_trailing_punct_keys(line)
            if REPLACE_NULL:
                line = re.sub(r':\s*null\b', ':""', line)

            try:
                obj = json.loads(line)
            except Exception as e:
                bad += 1
                print(f"[第{idx}行] 跳过（JSON 解析失败）: {e}", file=sys.stderr)
                continue

            # 解析后键名再规范一次
            renamed = {}
            for k, v in obj.items():
                k_fixed = KEY_NORMALIZE.get(k, k)
                renamed[k_fixed] = v

            # 先按固定顺序补齐，再进行成对裁剪
            ordered = OrderedDict()
            for k in KEEP_KEYS_ORDER:
                ordered[k] = renamed.get(k, "" if REPLACE_NULL else None)
            # 额外键保留
            for k, v in renamed.items():
                if k not in ordered:
                    ordered[k] = v

            ordered = prune_empty_role_fields(ordered)
            items.append(ordered)
    return items, bad

def dump_output(items):
    if WRAP_MODE == "object":
        out = {"data": items}
        path = OUT_DIR / "fixed_data.json"
    else:
        out = items
        path = OUT_DIR / "fixed.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    return str(path.resolve())

if __name__ == "__main__":
    if not INPUT.exists():
        print(f"找不到输入文件：{INPUT}")
        sys.exit(1)

    items, skipped = parse_jsonl(INPUT)
    out_path = dump_output(items)
    print(f"OK：有效 {len(items)} 条，跳过 {skipped} 条非 JSON/坏行。输出：{out_path}")
