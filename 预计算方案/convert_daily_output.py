"""
将每日输出格式转换为符合数据库格式的 JSON 文件
支持从多个 JSON 对象转换为完整的分析结果文件
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path(__file__).parent.parent

def parse_multiple_json_objects(text: str) -> List[Dict]:
    """
    从文本中解析多个独立的 JSON 对象
    支持多个 JSON 对象用换行分隔
    """
    objects = []
    
    # 使用正则表达式找到所有独立的 JSON 对象
    # 匹配从 { 开始到 } 结束的完整 JSON 对象
    pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    
    # 更简单的方法：按行分割，然后尝试解析每个 JSON 对象
    # 但更好的方法是找到完整的 JSON 对象
    current_obj = ""
    brace_count = 0
    in_string = False
    escape_next = False
    
    for char in text:
        if escape_next:
            escape_next = False
            current_obj += char
            continue
            
        if char == '\\':
            escape_next = True
            current_obj += char
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            
        if not in_string:
            if char == '{':
                if brace_count == 0:
                    current_obj = ""
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                
        current_obj += char
        
        # 当 brace_count 为 0 且不在字符串中时，说明一个完整的 JSON 对象结束了
        if brace_count == 0 and current_obj.strip() and not in_string:
            try:
                obj = json.loads(current_obj.strip())
                objects.append(obj)
            except json.JSONDecodeError as e:
                print(f"⚠️ 解析 JSON 对象时出错: {e}")
                print(f"   内容片段: {current_obj[:200]}...")
            current_obj = ""
    
    return objects

def calculate_summary(clusters: List[Dict]) -> Dict:
    """计算 summary 统计信息"""
    total_clusters = len(clusters)
    
    # 计算总玩家数和总发言数（可能有重复，但按格式应该是总和）
    total_players = sum(c.get("发言玩家总数", 0) for c in clusters)
    total_messages = sum(c.get("发言总数", 0) for c in clusters)
    
    # 找到热度最高的话题簇
    top_cluster = ""
    if clusters:
        top_cluster_obj = max(clusters, key=lambda x: x.get("热度评分", 0))
        top_cluster = top_cluster_obj.get("聚合话题簇", "")
    
    return {
        "total_clusters": total_clusters,
        "total_players": total_players,
        "total_messages": total_messages,
        "top_cluster": top_cluster
    }

def update_group_index(group_id: str, date: str, group_name: str = None):
    """
    更新对应群组的 index.json 文件
    
    Args:
        group_id: 群组ID ("1" 或 "2")
        date: 日期字符串 (格式: "YYYY-MM-DD")
        group_name: 群组名称（可选）
    """
    if group_name is None:
        group_name = f"地球群{group_id}"
    
    index_path = PROJECT_ROOT / "预计算方案" / "results" / f"group{group_id}" / "index.json"
    
    # 如果 index.json 不存在，创建新的
    if not index_path.exists():
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_data = {
            "group": group_name,
            "group_id": group_id,
            "updated_at": datetime.now().isoformat(),
            "available_dates": [date],
            "total_days": 1
        }
    else:
        # 读取现有的 index.json
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 更新日期列表（如果日期不存在，添加到列表开头）
        available_dates = index_data.get("available_dates", [])
        if date not in available_dates:
            available_dates.insert(0, date)  # 新日期添加到开头（最新的在前）
            index_data["available_dates"] = available_dates
            index_data["total_days"] = len(available_dates)
        
        # 更新更新时间
        index_data["updated_at"] = datetime.now().isoformat()
    
    # 保存更新后的 index.json
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    return index_path

def convert_to_result_format(clusters: List[Dict], group_id: str, date: str, group_name: str = None) -> Dict:
    """
    将话题簇列表转换为完整的结果格式
    
    Args:
        clusters: 话题簇列表
        group_id: 群组ID ("1" 或 "2")
        date: 日期字符串 (格式: "YYYY-MM-DD")
        group_name: 群组名称（可选，默认根据 group_id 生成）
    """
    if group_name is None:
        group_name = f"地球群{group_id}"
    
    return {
        "group": group_name,
        "group_id": group_id,
        "date": date,
        "generated_at": datetime.now().isoformat(),
        "clusters": clusters,
        "summary": calculate_summary(clusters)
    }

def process_input_file(input_path: str, output_path: str, group_id: str, date: str = None, group_name: str = None):
    """
    处理输入文件，转换为标准格式并保存
    
    Args:
        input_path: 输入文件路径（可以是文本文件或 JSON 文件）
        output_path: 输出文件路径
        group_id: 群组ID ("1" 或 "2")
        date: 日期字符串（如果为 None，会从 clusters 中提取）
        group_name: 群组名称（可选）
    """
    # 处理相对路径：如果文件不存在，尝试在预计算方案目录下查找
    input_file = Path(input_path)
    if not input_file.is_absolute():
        # 相对路径：先尝试当前目录，再尝试预计算方案目录
        if not input_file.exists():
            alt_path = PROJECT_ROOT / "预计算方案" / input_path
            if alt_path.exists():
                input_file = alt_path
            else:
                # 尝试直接在当前工作目录查找
                cwd_path = Path.cwd() / input_path
                if cwd_path.exists():
                    input_file = cwd_path
    
    if not input_file.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        print(f"   尝试查找路径:")
        print(f"   - {Path(input_path).absolute()}")
        print(f"   - {PROJECT_ROOT / '预计算方案' / input_path}")
        print(f"   - {Path.cwd() / input_path}")
        return False
    
    # 读取输入文件
    print(f"📖 读取文件: {input_path}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 JSON 对象
    print("🔍 解析 JSON 对象...")
    clusters = parse_multiple_json_objects(content)
    
    if not clusters:
        print("❌ 未找到有效的 JSON 对象")
        return False
    
    print(f"✅ 解析到 {len(clusters)} 个话题簇")
    
    # 如果没有指定日期，从第一个 cluster 中提取
    if date is None:
        first_cluster = clusters[0]
        date = first_cluster.get("日期", "")
        if not date:
            print("❌ 无法从数据中提取日期，请手动指定 date 参数")
            return False
        print(f"📅 从数据中提取日期: {date}")
    
    # 确保所有 cluster 的日期一致
    for cluster in clusters:
        cluster["日期"] = date
    
    # 转换为标准格式
    print("🔄 转换为标准格式...")
    result = convert_to_result_format(clusters, group_id, date, group_name)
    
    # 保存输出文件
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 保存到: {output_path}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 更新对应群组的 index.json
    print(f"\n📝 更新 group{group_id} 的 index.json...")
    index_path = update_group_index(group_id, date, group_name)
    print(f"✅ index.json 已更新: {index_path}")
    
    # 显示 summary 信息
    summary = result["summary"]
    print("\n" + "=" * 60)
    print("✅ 转换完成！")
    print("=" * 60)
    print(f"\n📊 Summary 信息:")
    print(f"  - total_clusters: {summary['total_clusters']}")
    print(f"  - total_players: {summary['total_players']}")
    print(f"  - total_messages: {summary['total_messages']}")
    print(f"  - top_cluster: {summary['top_cluster']}")
    print(f"\n💾 生成的文件:")
    print(f"  - 结果文件: {output_path}")
    print(f"  - 索引文件: {index_path}")
    
    return True

def main():
    """主函数 - 支持命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="将每日输出格式转换为标准 JSON 格式")
    parser.add_argument("input", help="输入文件路径（包含多个 JSON 对象的文本文件）")
    parser.add_argument("--output", "-o", help="输出文件路径（默认：预计算方案/results/group{group_id}/daily/{date}.json）")
    parser.add_argument("--group", "-g", required=True, choices=["1", "2"], help="群组ID (1 或 2)")
    parser.add_argument("--date", "-d", help="日期 (格式: YYYY-MM-DD，如果不指定会从数据中提取）")
    parser.add_argument("--name", "-n", help="群组名称（可选，默认：地球群{group_id}）")
    
    args = parser.parse_args()
    
    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        if not args.date:
            # 如果没指定日期，需要从输入文件中提取
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()
            clusters = parse_multiple_json_objects(content)
            if clusters:
                args.date = clusters[0].get("日期", "")
            else:
                print("❌ 无法确定日期，请使用 --date 参数指定")
                return
        
        # 使用绝对路径，确保无论从哪个目录运行都能正确输出到 daily 子目录
        output_path = str(PROJECT_ROOT / "预计算方案" / "results" / f"group{args.group}" / "daily" / f"{args.date}.json")
    
    # 处理文件
    success = process_input_file(
        args.input,
        output_path,
        args.group,
        args.date,
        args.name
    )
    
    if success:
        print("\n💡 下一步：运行以下命令推送到 GitHub")
        print(f"   python 预计算方案/push_results_to_github.py")
    else:
        sys.exit(1)

if __name__ == "__main__":
    # 如果直接运行且没有参数，显示使用说明
    if len(sys.argv) == 1:
        print("=" * 60)
        print("每日输出格式转换工具")
        print("=" * 60)
        print("\n使用方法：")
        print("  python convert_daily_output.py <输入文件> --group <1|2> [选项]")
        print("\n选项：")
        print("  --output, -o    输出文件路径（可选）")
        print("  --date, -d      日期 YYYY-MM-DD（可选，会从数据中提取）")
        print("  --name, -n      群组名称（可选）")
        print("\n示例：")
        print('  python convert_daily_output.py daily_output.txt --group 1 --date 2026-01-01')
        print('  python convert_daily_output.py group1_input.json --group 1')
        print("\n💡 提示：将你的 JSON 数据保存到文本文件，然后运行此脚本")
    else:
        main()
