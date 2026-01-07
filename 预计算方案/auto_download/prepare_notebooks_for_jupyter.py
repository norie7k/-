"""
为 Jupyter Notebook 运行准备配置
自动更新 top5_Q2_group1.ipynb 和 top5_Q2_group2.ipynb 的日期和文件路径

使用方法：
    python prepare_notebooks_for_jupyter.py              # 更新为昨天的日期
    python prepare_notebooks_for_jupyter.py --date 2025-12-24  # 指定日期
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta

from config import SOURCE_DIR, NOTEBOOKS


def update_notebook_config(notebook_path: Path, date_str: str, txt_pattern: str = None, mapping_file: str = None):
    """
    更新 Notebook 中的配置（日期、文件路径）
    
    Args:
        notebook_path: Notebook 文件路径
        date_str: 分析日期 (YYYY-MM-DD)
        txt_pattern: txt 文件名模式（如 "《欢迎来到地球》测试1群.txt"）
        mapping_file: mapping 文件名（如 "mapping地球1.xlsx"）
    """
    if not notebook_path.exists():
        print(f"❌ Notebook 不存在: {notebook_path}")
        return False
    
    # 读取 Notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # 构建时间范围
    start_time = f"{date_str} 00:00:00"
    next_day = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    end_time = f"{next_day} 00:00:00"
    
    # 查找实际的 txt 文件（支持日期前缀）
    actual_txt_file = None
    if txt_pattern:
        # 先尝试精确匹配
        txt_path = SOURCE_DIR / txt_pattern
        if txt_path.exists():
            actual_txt_file = txt_pattern
        else:
            # 尝试模式匹配（支持日期前缀）
            pattern = f"*{txt_pattern}"
            matches = list(SOURCE_DIR.glob(pattern))
            if matches:
                actual_txt_file = matches[0].name
                print(f"  📄 找到匹配文件: {actual_txt_file} (模式: {txt_pattern})")
            else:
                print(f"  ⚠️  未找到匹配的 txt 文件: {txt_pattern}")
                actual_txt_file = txt_pattern  # 使用原始文件名
    
    # 更新每个 cell 中的配置
    updated = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source_lines = cell.get("source", [])
            if isinstance(source_lines, str):
                source_lines = [source_lines]
            
            new_lines = []
            for line in source_lines:
                original_line = line
                
                # 更新 start_time
                if re.match(r'^start_time\s*=\s*["\']', line):
                    line = f'start_time = "{start_time}"\n'
                    updated = True
                
                # 更新 end_time
                elif re.match(r'^end_time\s*=\s*["\']', line):
                    line = f'end_time = "{end_time}"\n'
                    updated = True
                
                # 更新 pathtxt（如果提供了 txt_pattern）
                elif actual_txt_file and re.match(r'^pathtxt\s*=\s*["\']', line):
                    line = f'pathtxt = "{actual_txt_file}"\n'
                    updated = True
                
                # 更新 MAPPING_FILE（如果提供了 mapping_file）
                elif mapping_file and re.match(r'^MAPPING_FILE\s*=\s*["\']', line):
                    line = f'MAPPING_FILE = "{mapping_file}"\n'
                    updated = True
                
                new_lines.append(line)
            
            cell["source"] = new_lines
    
    if updated:
        # 保存更新后的 Notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        return True
    else:
        print(f"  ⚠️  未找到需要更新的配置项")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="为 Jupyter Notebook 运行准备配置")
    parser.add_argument("--date", type=str, help="分析日期 (YYYY-MM-DD)，默认为昨天")
    args = parser.parse_args()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("📝 为 Jupyter Notebook 准备配置")
    print("=" * 60)
    print(f"📅 分析日期: {date_str}")
    print()
    
    # 更新每个 Notebook
    success_count = 0
    for nb_config in NOTEBOOKS:
        name = nb_config["name"]
        notebook_path = nb_config["notebook"]
        mapping_file = nb_config.get("mapping_file")
        txt_pattern = nb_config.get("txt_pattern")
        
        print(f"\n📘 {name}")
        print(f"   Notebook: {notebook_path.name}")
        
        if update_notebook_config(notebook_path, date_str, txt_pattern, mapping_file):
            print(f"   ✅ 配置已更新")
            success_count += 1
        else:
            print(f"   ⚠️  配置更新失败或无需更新")
    
    print("\n" + "=" * 60)
    if success_count == len(NOTEBOOKS):
        print("✅ 所有 Notebook 配置已更新完成！")
        print("=" * 60)
        print("\n📌 下一步：")
        print("1. 在 Jupyter Notebook 中打开这两个文件")
        print("2. 依次运行所有 cell（Kernel → Restart & Run All）")
        print("3. 等待执行完成（可能需要 5 小时+）")
        print("4. 复制输出的 JSON 结果")
        print("5. 使用 save_results.py 保存结果")
    else:
        print("⚠️  部分 Notebook 配置更新失败")
        print("=" * 60)


if __name__ == "__main__":
    main()

