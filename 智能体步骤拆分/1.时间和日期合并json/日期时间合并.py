# -*- coding: utf-8 -*-
from pathlib import Path
import json, sys

# ===== 修改为你的实际路径 =====
INPUT_FILE  = r"E:\项目\玩家社群分析智能体\地球806全天.jsonl"         # 输入 JSONL
OUTPUT_FILE = r"E:\项目\玩家社群分析智能体\地球806全天new.jsonl"   # 输出 JSONL
ENCODING    = "utf-8-sig"
KEEP_OLD    = False   # True=保留原字段“发言日期/发言时间”；False=删除
TIME_KEY    = "时间"   # 若想直接叫 TI，可改为 "TI"
# =================================

def main():
    in_path  = Path(INPUT_FILE)
    out_path = Path(OUTPUT_FILE)

    if not in_path.exists():
        print(f"[ERROR] 输入不存在：{in_path}", file=sys.stderr); sys.exit(1)

    total = 0
    updated = 0

    with in_path.open("r", encoding=ENCODING) as fin, \
         out_path.open("w", encoding="utf-8") as fout:

        for lineno, line in enumerate(fin, start=1):
            s = line.strip()
            if not s:
                continue
            total += 1
            try:
                obj = json.loads(s)
            except Exception as e:
                print(f"[WARN] 第 {lineno} 行不是合法 JSON：{e}", file=sys.stderr)
                continue

            date = str(obj.get("发言日期", "")).strip()
            time = str(obj.get("发言时间", "")).strip()

            # ---- 构造“时间优先”的有序对象 ----
            new_obj = {}

            # 1) 先放“时间”
            if date and time:
                new_obj[TIME_KEY] = f"{date} {time}"
                updated += 1
            else:
                # 如果缺日期或时间，也可以不生成“时间”；按需保留空值：
                # new_obj[TIME_KEY] = ""
                pass

            # 2) 其他字段按原顺序追加（可选择是否保留旧的两个字段）
            for k, v in obj.items():
                if k in ("发言日期", "发言时间") and not KEEP_OLD:
                    continue
                # 如果我们已经放了 TIME_KEY 且 k==TIME_KEY，跳过避免重复
                if k == TIME_KEY and TIME_KEY in new_obj:
                    continue
                new_obj[k] = v

            # 3) 若 KEEP_OLD=True 且 new_obj 里还没有原字段（比如最前面没生成“时间”），也保留其原顺序
            # （上面的循环已经处理，这里无需额外代码）

            fout.write(json.dumps(new_obj, ensure_ascii=False) + "\n")

    print(f"[OK] 已处理 {total} 行，其中合并成功 {updated} 行。输出：{out_path.resolve()}")

if __name__ == "__main__":
    main()
