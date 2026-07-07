"""
版本分析输出格式转换工具
将原始版本输出格式转换为标准的 version JSON 格式
使用方法类似 convert_daily_output.py
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def extract_days_from_text(text):
    """
    从文本中提取天数
    例如：'3天（2026-01-02、2026-01-12、2026-01-14）' → 3
    """
    match = re.search(r'(\d+)天', text)
    return int(match.group(1)) if match else 0

def extract_date_range(text):
    """
    从文本中提取日期范围
    例如：'3天（2026-01-02、2026-01-12、2026-01-14）' → '2026-01-02 ~ 2026-01-14'
    或：'2天（2026-01-04 ~ 2026-01-05）' → '2026-01-04 ~ 2026-01-05'
    """
    # 先尝试匹配范围格式：2026-01-04 ~ 2026-01-05
    range_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})', text)
    if range_match:
        return f"{range_match.group(1)} ~ {range_match.group(2)}"
    
    # 如果没有范围，尝试提取所有日期
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
    if len(dates) >= 2:
        return f"{dates[0]} ~ {dates[-1]}"
    elif len(dates) == 1:
        return f"{dates[0]} ~ {dates[0]}"
    
    return ""

def convert_discussion_points(discussion_list):
    """
    转换讨论点列表格式
    """
    points = []
    
    for item in discussion_list:
        # 查找讨论点的键（讨论点1、讨论点2等）
        point_text = ""
        for key in item.keys():
            if key.startswith('讨论点'):
                point_text = item[key]
                break
        
        if not point_text:
            continue
        
        point_data = {
            "point": point_text,
            "opinions": item.get('玩家观点', []),
            "examples": item.get('代表性玩家发言示例', [])
        }
        points.append(point_data)
    
    return points

def parse_raw_data(content):
    """
    解析原始数据（支持 JSON 数组、Python 字典格式等）
    """
    content = content.strip()
    
    # 尝试解析为标准 JSON 数组
    if content.startswith('['):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    
    # 尝试解析为标准 JSON 对象
    if content.startswith('{'):
        try:
            data = json.loads(content)
            # 如果是字典，尝试找到话题列表
            if isinstance(data, dict):
                for key in ['topics', '话题列表', 'data', 'clusters', '话提簇']:
                    if key in data:
                        return data[key]
                return [data]
            return [data]
        except json.JSONDecodeError:
            pass
    
    # 尝试解析为 Python 字典格式（使用 ast.literal_eval）
    try:
        import ast
        # 尝试将整个内容包装成列表（如果是多个字典用逗号分隔）
        if content.startswith('{') and not content.startswith('['):
            # 包装成列表
            list_content = '[' + content + ']'
            data = ast.literal_eval(list_content)
            if isinstance(data, list):
                return data
        else:
            data = ast.literal_eval(content)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
    except (ValueError, SyntaxError) as e:
        print(f"⚠️ Python 字典格式解析失败: {e}")
    
    # 尝试分割多个 JSON 对象（用逗号或换行分隔）
    try:
        if '},{' in content:
            objects_str = '[' + content + ']'
            return json.loads(objects_str)
    except json.JSONDecodeError:
        pass
    
    print("❌ 无法解析输入数据")
    print("💡 支持的格式：")
    print("  1. JSON 数组: [{...}, {...}]")
    print("  2. Python 字典: {...}, {...}")
    print("  3. 单个对象: {...}")
    return None

def convert_raw_to_version_format(raw_data, version_name, period, group, source="QQ"):
    """
    将原始数据转换为标准版本格式
    
    Parameters:
        raw_data: 原始数据列表（每个元素包含话提簇标题、讨论热度等）
        version_name: 版本名称（如 "beta15_旋转木马测试"）
        period: 版本周期（如 "2025-12-03 ~ 2025-12-17"）
        group: 群名称（如 "地球群1"）
        source: 数据来源（默认 "QQ"）
    
    Returns:
        dict: 标准格式的版本数据
    """
    topics = []
    
    for rank, topic_data in enumerate(raw_data, start=1):
        # 提取基本信息
        title = topic_data.get('话提簇标题', '')
        heat_info = topic_data.get('讨论热度（量化）', {})
        
        # 提取热度数据
        discussion_days_text = heat_info.get('讨论覆盖天数', '0天')
        discussion_days = extract_days_from_text(discussion_days_text)
        # 保留原始格式的日期范围文本
        date_range = discussion_days_text
        
        total_players = heat_info.get('发言玩家总数', 0)
        total_messages = heat_info.get('发言总量', 0)
        heat_score = heat_info.get('热度值', 0.0)
        heat_trend = heat_info.get('热度趋势', '')
        
        # 转换讨论点
        discussion_points = convert_discussion_points(
            topic_data.get('讨论点列表', [])
        )
        
        # 构建话题数据
        topic = {
            "rank": rank,
            "title": title,
            "heat_score": heat_score,
            "discussion_days": discussion_days,
            "date_range": date_range,
            "total_players": total_players,
            "total_messages": total_messages,
            "heat_trend": heat_trend,
            "discussion_points": discussion_points
        }
        
        topics.append(topic)
    
    # 构建完整的版本数据
    version_data = {
        "version": version_name,
        "period": period,
        "group": group,
        "source": source,
        "topics": topics
    }
    
    return version_data

def update_group_index(group_id, version_id):
    """
    更新群组的 index.json 文件，添加新的版本
    """
    index_path = PROJECT_ROOT / "预计算方案" / "results" / f"group{group_id}" / "index.json"
    
    # 读取现有索引
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = {
            "available_dates": [],
            "available_versions": [],
            "total_days": 0,
            "updated_at": ""
        }
    
    # 添加版本（如果不存在）
    if version_id not in index_data["available_versions"]:
        index_data["available_versions"].append(version_id)
        index_data["available_versions"].sort()
    
    # 更新时间戳
    index_data["updated_at"] = datetime.now().isoformat()
    
    # 保存索引
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    return index_path

def process_input_file(input_path, output_path, group_id, version_name, version_id, period, group_name=None):
    """
    处理输入文件并生成标准格式的 JSON
    
    Parameters:
        input_path: 输入文件路径
        output_path: 输出文件路径
        group_id: 群组ID（1或2）
        version_name: 版本完整名称（如 "beta15_旋转木马测试"）
        version_id: 版本ID（如 "beta15"，用于文件名）
        period: 版本周期（如 "2025-12-03 ~ 2025-12-17"）
        group_name: 群组名称（可选）
    """
    print("=" * 60)
    print("版本分析输出格式转换")
    print("=" * 60)
    print()
    
    # 读取输入文件
    print(f"📖 读取输入文件: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_path}")
        return False
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    # 解析原始数据
    print(f"🔄 解析原始数据...")
    raw_data = parse_raw_data(content)
    
    if not raw_data:
        return False
    
    print(f"✅ 成功解析 {len(raw_data)} 个话题簇")
    print()
    
    # 确定群组名称
    if not group_name:
        group_name = f"地球群{group_id}"
    
    # 转换为标准格式
    print(f"🔄 转换为标准格式...")
    print(f"  - 版本: {version_name}")
    print(f"  - 周期: {period}")
    print(f"  - 群组: {group_name}")
    print(f"  - 来源: QQ")
    print()
    
    version_data = convert_raw_to_version_format(
        raw_data=raw_data,
        version_name=version_name,
        period=period,
        group=group_name,
        source="QQ"
    )
    
    # 保存到文件
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 保存到文件: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(version_data, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    print(f"📋 更新索引文件...")
    index_path = update_group_index(group_id, version_id)
    
    # 生成统计摘要
    total_topics = len(version_data["topics"])
    total_players = sum(t["total_players"] for t in version_data["topics"])
    total_messages = sum(t["total_messages"] for t in version_data["topics"])
    top_topic = version_data["topics"][0]["title"] if version_data["topics"] else "无"
    
    print()
    print("=" * 60)
    print("✅ 转换成功！")
    print("=" * 60)
    print()
    print(f"📊 数据摘要:")
    print(f"  - 版本名称: {version_name}")
    print(f"  - 版本周期: {period}")
    print(f"  - 话题总数: {total_topics}")
    print(f"  - 参与玩家: {total_players}")
    print(f"  - 发言总量: {total_messages}")
    print(f"  - 热门话题: {top_topic}")
    print(f"\n💾 生成的文件:")
    print(f"  - 结果文件: {output_path}")
    print(f"  - 索引文件: {index_path}")
    
    return True

def main():
    """主函数 - 支持命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="将版本输出格式转换为标准 JSON 格式")
    parser.add_argument("--input", "-i", default="预计算方案/version.txt", help="输入文件路径（默认：预计算方案/version.txt）")
    parser.add_argument("--output", "-o", help="输出文件路径（默认：预计算方案/results/group{group_id}/version/{version_id}.json）")
    parser.add_argument("--group", "-g", required=True, choices=["1", "2"], help="群组ID (1 或 2)")
    parser.add_argument("--version", "-v", required=True, help="版本ID（如 beta15，用于文件名）")
    parser.add_argument("--version-name", "-vn", help="版本完整名称（如 beta15_旋转木马测试，默认使用 --version 的值）")
    parser.add_argument("--period", "-p", required=True, help="版本周期（格式: YYYY-MM-DD ~ YYYY-MM-DD）")
    parser.add_argument("--name", "-n", help="群组名称（可选，默认：地球群{group_id}）")
    
    args = parser.parse_args()
    
    # 确定版本完整名称
    version_name = args.version_name if args.version_name else args.version
    
    # 确定输入路径（支持相对路径和绝对路径）
    input_path = args.input
    if not Path(input_path).is_absolute():
        input_path = str(PROJECT_ROOT / input_path)
    
    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        output_path = str(PROJECT_ROOT / "预计算方案" / "results" / f"group{args.group}" / "version" / f"{args.version}.json")
    
    # 处理文件
    success = process_input_file(
        input_path,
        output_path,
        args.group,
        version_name,
        args.version,
        args.period,
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
        print("版本分析输出格式转换工具")
        print("=" * 60)
        print("\n使用方法：")
        print("  python convert_version_output.py --group <1|2> --version <版本ID> --period <周期> [选项]")
        print("\n必需参数：")
        print("  --group, -g         群组ID (1 或 2)")
        print("  --version, -v       版本ID（如 beta16，用于文件名）")
        print("  --period, -p        版本周期（如 2026-01-01 ~ 2026-01-15）")
        print("\n可选参数：")
        print("  --input, -i         输入文件路径（默认：预计算方案/version.txt）")
        print("  --output, -o        输出文件路径（默认：自动生成）")
        print("  --version-name, -vn 版本完整名称（如 beta16_新年测试）")
        print("  --name, -n          群组名称（默认：地球群{group_id}）")
        print("\n示例：")
        print('  # 使用默认输入文件（预计算方案/version.txt）')
        print('  python convert_version_output.py -g 1 -v beta16 -p "2026-01-01 ~ 2026-01-15"')
        print()
        print('  # 带完整版本名称')
        print('  python convert_version_output.py -g 1 -v beta16 -vn "beta16_新年测试" -p "2026-01-01 ~ 2026-01-15"')
        print()
        print('  # 指定自定义输入文件')
        print('  python convert_version_output.py -i custom.txt -g 2 -v beta16 -p "2026-01-01 ~ 2026-01-15"')
        print("\n💡 提示：")
        print("  1. 将版本分析数据保存到 预计算方案/version.txt")
        print("  2. 数据格式应包含：话提簇标题、讨论热度（量化）、讨论点列表")
        print("  3. 运行此脚本自动转换为标准格式")
        print("  4. 文件会自动保存到 results/group{id}/version/{version}.json")
        print("=" * 60)
    else:
        main()
