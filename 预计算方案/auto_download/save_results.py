"""
将分析结果按群分别保存到 results 目录并推送到 GitHub

结构:
    results/
    ├── group1/          # 群1 每日结果
    │   ├── index.json
    │   └── 2025-12-17.json
    ├── group2/          # 群2 每日结果
    │   ├── index.json
    │   └── 2025-12-17.json
    └── index.json       # 总索引

使用方式:
    # 保存群1今天的结果（粘贴模式）
    python save_results.py --group 1 --paste
    
    # 保存群2今天的结果（粘贴模式）
    python save_results.py --group 2 --paste
    
    # 保存后推送到 GitHub
    python save_results.py --group 1 --paste --push
    
    # 从文件读取保存
    python save_results.py --group 1 --file output.json --push
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = PROJECT_ROOT / "玩家发言整理（供运营侧）" / "玩家发言总结_版本总结V2-Copy1.0(单日）"
RESULTS_DIR = PROJECT_ROOT / "预计算方案" / "results"

# 群配置
GROUPS = {
    "1": {"name": "地球群1", "dir": "group1"},
    "2": {"name": "地球群2", "dir": "group2"},
}


def get_group_dir(group_id: str) -> Path:
    """获取群的结果目录"""
    group = GROUPS.get(group_id)
    if not group:
        raise ValueError(f"未知的群ID: {group_id}")
    return RESULTS_DIR / group["dir"]


def save_from_paste(group_id: str) -> bool:
    """
    从粘贴的 JSON 内容保存结果
    """
    group = GROUPS.get(group_id)
    if not group:
        print(f"❌ 未知的群ID: {group_id}")
        return False
    
    print("=" * 60)
    print(f"📋 粘贴模式 - 保存 {group['name']} 的结果")
    print("=" * 60)
    print()
    print("请粘贴 Notebook 输出的 JSON 内容")
    print("(支持多个 JSON 对象，输入空行两次结束)")
    print("-" * 40)
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    
    content = "\n".join(lines)
    
    if not content.strip():
        print("❌ 没有输入内容")
        return False
    
    # 解析 JSON
    results = parse_json_content(content)
    
    if not results:
        print("❌ 未能解析出有效的 JSON 数据")
        return False
    
    # 保存结果
    return save_results_to_group(group_id, results)


def save_from_file(group_id: str, file_path: Path) -> bool:
    """从文件读取并保存结果"""
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    print(f"📄 从文件读取: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = parse_json_content(content)
    
    if not results:
        print("❌ 未能解析出有效的 JSON 数据")
        return False
    
    return save_results_to_group(group_id, results)


def parse_json_content(content: str) -> list:
    """解析 JSON 内容（支持多种格式）"""
    results = []
    
    # 尝试作为单个 JSON 数组解析
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        else:
            return [data]
    except json.JSONDecodeError:
        pass
    
    # 尝试按 }{ 分割（多个连续 JSON 对象）
    content_fixed = content.replace("}\n{", "}|||{").replace("}{", "}|||{")
    parts = content_fixed.split("|||")
    
    for part in parts:
        part = part.strip()
        if part:
            try:
                results.append(json.loads(part))
            except json.JSONDecodeError:
                # 尝试 JSONL 格式（每行一个 JSON）
                for line in part.split("\n"):
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except:
                            continue
    
    return results


def save_results_to_group(group_id: str, results: list) -> bool:
    """保存结果到指定群的目录"""
    group = GROUPS.get(group_id)
    group_dir = get_group_dir(group_id)
    group_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ 解析到 {len(results)} 条记录")
    
    # 按日期分组
    by_date = defaultdict(list)
    for record in results:
        date = record.get("日期", "unknown")
        by_date[date].append(record)
    
    print(f"📅 包含 {len(by_date)} 个日期的数据:")
    for date in sorted(by_date.keys()):
        print(f"   {date}: {len(by_date[date])} 条话题簇")
    
    # 保存每日结果
    saved_files = []
    for date in sorted(by_date.keys()):
        if date == "unknown":
            continue
        
        clusters = by_date[date]
        
        # 构建结果
        result = {
            "group": group["name"],
            "group_id": group_id,
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "clusters": clusters,
            "summary": {
                "total_clusters": len(clusters),
                "total_players": sum(c.get("发言玩家总数", 0) for c in clusters),
                "total_messages": sum(c.get("发言总数", 0) for c in clusters),
                "top_cluster": max(clusters, key=lambda x: x.get("热度评分", 0)).get("聚合话题簇", "") if clusters else "",
            }
        }
        
        # 保存
        output_file = group_dir / f"{date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存: {group['dir']}/{date}.json")
        saved_files.append(output_file)
    
    # 更新群索引
    update_group_index(group_id)
    
    # 更新总索引
    update_main_index()
    
    print(f"\n📊 {group['name']} 共保存 {len(saved_files)} 个日期的结果")
    return True


def update_group_index(group_id: str):
    """更新群的索引文件"""
    group = GROUPS.get(group_id)
    group_dir = get_group_dir(group_id)
    
    # 扫描所有日期文件
    dates = []
    for f in group_dir.glob("*.json"):
        if f.name != "index.json":
            dates.append(f.stem)
    
    index = {
        "group": group["name"],
        "group_id": group_id,
        "updated_at": datetime.now().isoformat(),
        "available_dates": sorted(dates, reverse=True),  # 最新日期在前
        "total_days": len(dates),
    }
    
    index_file = group_dir / "index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def update_main_index():
    """更新总索引文件"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    groups_info = []
    all_dates = set()
    
    for group_id, group in GROUPS.items():
        group_dir = RESULTS_DIR / group["dir"]
        if group_dir.exists():
            index_file = group_dir / "index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    group_index = json.load(f)
                    groups_info.append({
                        "group_id": group_id,
                        "name": group["name"],
                        "total_days": group_index.get("total_days", 0),
                        "latest_date": group_index.get("available_dates", [""])[0] if group_index.get("available_dates") else "",
                    })
                    all_dates.update(group_index.get("available_dates", []))
    
    index = {
        "updated_at": datetime.now().isoformat(),
        "groups": groups_info,
        "all_dates": sorted(all_dates, reverse=True),
        "total_days": len(all_dates),
    }
    
    index_file = RESULTS_DIR / "index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新总索引")


def git_push():
    """推送到 GitHub"""
    print()
    print("=" * 60)
    print("🚀 推送到 GitHub")
    print("=" * 60)
    print()
    
    try:
        os.chdir(PROJECT_ROOT)
        
        # git add
        subprocess.run(["git", "add", "预计算方案/results/"], check=True)
        print("✅ git add 完成")
        
        # git commit
        commit_msg = f"[自动] 更新分析结果 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ git commit 完成: {commit_msg}")
        else:
            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                print("ℹ️ 没有新的更改需要提交")
                return True
            else:
                print(f"⚠️ commit 输出: {result.stderr or result.stdout}")
        
        # git push
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ git push 完成!")
            return True
        else:
            print(f"❌ push 失败: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="保存群分析结果到 results 目录")
    parser.add_argument("--group", "-g", type=str, required=True, choices=["1", "2"],
                       help="群ID: 1=地球群1, 2=地球群2")
    parser.add_argument("--paste", "-p", action="store_true", 
                       help="粘贴模式：直接粘贴 JSON 内容保存")
    parser.add_argument("--file", "-f", type=str, 
                       help="从指定文件读取结果")
    parser.add_argument("--push", action="store_true", 
                       help="保存后推送到 GitHub")
    args = parser.parse_args()
    
    success = False
    
    if args.paste:
        success = save_from_paste(args.group)
    elif args.file:
        success = save_from_file(args.group, Path(args.file))
    else:
        print("❌ 请指定 --paste 或 --file 参数")
        parser.print_help()
        sys.exit(1)
    
    if success and args.push:
        git_push()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 完成!")
    else:
        print("❌ 操作失败")
    print("=" * 60)


if __name__ == "__main__":
    main()
