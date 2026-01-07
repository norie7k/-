"""验证 JSON 文件格式"""
import json
import sys
from pathlib import Path

file_path = Path("预计算方案/results/group1_input.json")

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ JSON 格式正确！")
    print(f"   共 {len(data)} 条记录")
    print(f"   日期范围: {min(item.get('日期', '') for item in data)} 到 {max(item.get('日期', '') for item in data)}")
    sys.exit(0)
except json.JSONDecodeError as e:
    print(f"❌ JSON 格式错误:")
    print(f"   行 {e.lineno}, 列 {e.colno}: {e.msg}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)

