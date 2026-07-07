"""
从文件转换AI输出到Streamlit格式的每日JSON文件

用法：
1. 将AI输出保存到 input_daily.json 文件
2. 运行此脚本
3. 选择群组（1或2）
"""
import json
from pathlib import Path
from datetime import datetime

# ==================== 配置 ====================

# 输入文件（AI输出的JSON列表）
INPUT_FILE = Path(__file__).parent / "input_daily.json"

# 输出目录
RESULTS_DIR = Path(__file__).parent / "results2"

# 群名称映射
GROUP_NAMES = {
    "1": "地球群1",
    "2": "地球群2"
}

# ==================== 转换逻辑 ====================

def extract_date_from_clusters(clusters: list) -> str:
    """从聚合话题簇中提取日期"""
    for cluster in clusters:
        date = cluster.get("日期", "")
        if date:
            return date
    return datetime.now().strftime("%Y-%m-%d")

def calculate_summary(clusters: list) -> dict:
    """计算统计摘要"""
    total_players = set()
    total_messages = 0
    top_cluster = ""
    top_heat = 0
    
    for cluster in clusters:
        total_messages += cluster.get("发言总数", 0)
        
        discussion_list = cluster.get("讨论点列表", [])
        for dp in discussion_list:
            opinion_list = dp.get("观点列表", [])
            for opinion in opinion_list:
                raw_msgs = opinion.get("原文发言", [])
                for msg in raw_msgs:
                    player_id = msg.get("玩家ID", "")
                    if player_id:
                        total_players.add(player_id)
        
        heat = cluster.get("热度评分", 0)
        if heat > top_heat:
            top_heat = heat
            top_cluster = cluster.get("聚合话题簇", "")
    
    if not total_players:
        total_players_count = sum(c.get("发言玩家总数", 0) for c in clusters)
    else:
        total_players_count = len(total_players)
    
    return {
        "total_clusters": len(clusters),
        "total_players": total_players_count,
        "total_messages": total_messages,
        "top_cluster": top_cluster
    }

def convert_to_streamlit_format(clusters: list, group_id: str) -> dict:
    """将AI输出转换为Streamlit格式"""
    date = extract_date_from_clusters(clusters)
    summary = calculate_summary(clusters)
    
    return {
        "group": GROUP_NAMES.get(group_id, f"地球群{group_id}"),
        "group_id": group_id,
        "date": date,
        "generated_at": datetime.now().isoformat(),
        "source": "QQ",
        "clusters": clusters,
        "summary": summary
    }

def update_index(group_id: str, date: str):
    """更新index.json"""
    group_dir = RESULTS_DIR / f"group{group_id}"
    index_file = group_dir / "index.json"
    
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    else:
        index_data = {
            "group": GROUP_NAMES.get(group_id, f"地球群{group_id}"),
            "group_id": group_id,
            "available_dates": [],
            "available_versions": [],
            "last_updated": ""
        }
    
    if date not in index_data.get("available_dates", []):
        index_data["available_dates"].append(date)
        index_data["available_dates"] = sorted(index_data["available_dates"], reverse=True)
    
    index_data["last_updated"] = datetime.now().isoformat()
    
    # 确保目录存在
    group_dir.mkdir(parents=True, exist_ok=True)
    
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 更新 index.json（共 {len(index_data['available_dates'])} 天数据）")

def save_daily_json(data: dict, group_id: str, date: str):
    """保存每日JSON文件"""
    group_dir = RESULTS_DIR / f"group{group_id}"
    daily_dir = group_dir / "daily"
    
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = daily_dir / f"{date}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 保存 {output_file}")
    return output_file

def main():
    print("=" * 60)
    print("转换AI输出到Streamlit格式（从文件读取）")
    print("=" * 60)
    
    # 检查输入文件
    if not INPUT_FILE.exists():
        print(f"\n⚠️ 输入文件不存在: {INPUT_FILE}")
        print("\n请将AI输出保存到该文件，格式为JSON列表：")
        print('[')
        print('  {"聚合话题簇": "...", "日期": "2026-01-27", ...},')
        print('  {"聚合话题簇": "...", ...}')
        print(']')
        
        # 创建示例文件
        example_data = [
            {
                "聚合话题簇": "示例话题",
                "日期": "2026-01-27",
                "时间轴": "09:00:00-10:00:00",
                "发言玩家总数": 5,
                "发言总数": 20,
                "热度评分": 50.0,
                "讨论点列表": []
            }
        ]
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(example_data, f, ensure_ascii=False, indent=2)
        print(f"\n已创建示例文件: {INPUT_FILE}")
        print("请替换为实际数据后重新运行")
        return
    
    # 读取输入文件
    print(f"\n📂 读取输入文件: {INPUT_FILE}")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON解析错误: {e}")
        print("请检查文件格式是否正确")
        return
    
    if not input_data:
        print("\n⚠️ 输入文件为空")
        return
    
    print(f"📊 检测到 {len(input_data)} 个话题簇")
    
    # 提取日期
    date = extract_date_from_clusters(input_data)
    print(f"📅 日期: {date}")
    
    # 选择群组
    print("\n请选择群组:")
    print("  1 = 地球群1")
    print("  2 = 地球群2")
    
    while True:
        group_id = input("输入群组编号 (1/2): ").strip()
        if group_id in ["1", "2"]:
            break
        print("请输入 1 或 2")
    
    print(f"🏠 群组: {GROUP_NAMES.get(group_id)}")
    
    # 转换格式
    print("\n🔄 转换中...")
    streamlit_data = convert_to_streamlit_format(input_data, group_id)
    
    # 显示摘要
    summary = streamlit_data["summary"]
    print(f"\n📈 统计摘要:")
    print(f"  - 话题簇数: {summary['total_clusters']}")
    print(f"  - 玩家数: {summary['total_players']}")
    print(f"  - 发言数: {summary['total_messages']}")
    print(f"  - 最热话题: {summary['top_cluster']}")
    
    # 保存文件
    print("\n💾 保存文件...")
    output_file = save_daily_json(streamlit_data, group_id, date)
    
    # 更新索引
    update_index(group_id, date)
    
    print("\n" + "=" * 60)
    print("✅ 转换完成！")
    print("=" * 60)
    print(f"\n📁 输出文件: {output_file}")
    print("\n下一步:")
    print("1. 运行 push_app2_to_github.py 推送到GitHub")
    print("2. 在Streamlit Cloud查看结果")

if __name__ == "__main__":
    main()
