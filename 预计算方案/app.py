"""
玩家社群分析 - 历史结果查询
Streamlit 应用：查看每日群聊分析结果（从 GitHub 读取）
显示格式与 H5包装保持一致
"""
import streamlit as st
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 ====================

# GitHub 原始文件 URL
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/norie7k/-/main/预计算方案/results"

# 本地结果目录（开发时使用）
LOCAL_RESULTS_DIR = Path(__file__).parent / "results"

# 群配置
GROUPS = {
    "1": {"name": "🌍 地球群1", "dir": "group1"},
    "2": {"name": "🌎 地球群2", "dir": "group2"},
}

# ==================== CSS 样式（与 H5包装一致）===================

STYLE_CSS = """
<style>
.stats-overview {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 2rem;
}

.stats-overview h2 {
    color: white;
    margin-bottom: 1.5rem;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}

.stat-item {
    background: rgba(255, 255, 255, 0.2);
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

.discussion-point {
    background: #f0f2f6;
    padding: 1rem;
    border-left: 4px solid #667eea;
    margin: 1rem 0;
    border-radius: 4px;
}

.opinion-item {
    background: #fff;
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    border-left: 3px solid #4CAF50;
}

.example-quote {
    background: #e3f2fd;
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    border-left: 3px solid #2196F3;
    font-style: italic;
    color: #1976D2;
}
</style>
"""

# ==================== 数据加载 ====================

@st.cache_data(ttl=300)  # 缓存5分钟
def load_index(group_id: str) -> dict:
    """加载群的索引文件"""
    group = GROUPS.get(group_id)
    if not group:
        return {}
    
    # 优先尝试本地文件
    local_path = LOCAL_RESULTS_DIR / group["dir"] / "index.json"
    if local_path.exists():
        with open(local_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 尝试从 GitHub 加载
    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/index.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"加载索引失败: {e}")
    
    return {}


@st.cache_data(ttl=300)
def load_result(group_id: str, date: str) -> dict:
    """加载指定日期的分析结果"""
    group = GROUPS.get(group_id)
    if not group:
        return {}
    
    # 优先尝试本地文件
    local_path = LOCAL_RESULTS_DIR / group["dir"] / f"{date}.json"
    if local_path.exists():
        with open(local_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 尝试从 GitHub 加载
    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/{date}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"加载数据失败: {e}")
    
    return {}


# ==================== 渲染函数（与 H5包装格式一致）===================

def render_result(result: dict):
    """渲染分析结果 - 格式与 H5包装一致"""
    if not result:
        st.warning("⚠️ 暂无数据")
        return
    
    date = result.get("date", "")
    clusters = result.get("clusters", [])
    summary = result.get("summary", {})
    
    # 统计概览（与 H5包装格式一致）
    total_clusters = summary.get("total_clusters", len(clusters))
    total_players = summary.get("total_players", 0)
    total_messages = summary.get("total_messages", 0)
    
    st.markdown(f"""
    <div class="stats-overview">
        <h2>📊 {date} 分析报告</h2>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-value">{total_messages}</div>
                <div class="stat-label">总发言数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_players}</div>
                <div class="stat-label">参与玩家数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{total_clusters}</div>
                <div class="stat-label">热门话题簇</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 热门话题簇详情（与 H5包装格式一致）
    st.markdown("### 🔥 热门话题 Top 5")
    
    # 按热度排序
    sorted_clusters = sorted(clusters, key=lambda x: x.get("热度评分", 0), reverse=True)
    
    for idx, cluster in enumerate(sorted_clusters[:5], 1):  # 只显示 Top 5
        with st.expander(f"#{idx} {cluster['聚合话题簇']}", expanded=(idx <= 2)):
            # 基本信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("热度评分", f"{cluster['热度评分']:.1f} 🔥")
            with col2:
                st.metric("发言玩家数", cluster['发言玩家总数'])
            with col3:
                st.metric("发言总数", cluster['发言总数'])
            
            st.markdown(f"**⏰ 时间轴:** {cluster['时间轴']}")
            
            # 讨论点列表（与 H5包装格式一致）
            discussion_list = cluster.get('讨论点列表', [])
            if discussion_list:
                st.markdown("#### 💬 讨论点与玩家观点")
                
                for dp in discussion_list:
                    # 获取讨论点标题
                    dp_title = ""
                    for key in dp.keys():
                        if key.startswith("讨论点"):
                            dp_title = dp[key]
                            break
                    
                    if dp_title:
                        st.markdown(f"""
                        <div class="discussion-point">
                            <strong>📌 {dp_title}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 玩家观点
                    opinions = dp.get('玩家观点', [])
                    if opinions:
                        st.markdown("**玩家观点:**")
                        for opinion in opinions:
                            st.markdown(f"""
                            <div class="opinion-item">
                                {opinion}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 代表性发言
                    examples = dp.get('代表性玩家发言示例', [])
                    if examples:
                        st.markdown("**代表性发言:**")
                        for example in examples:
                            st.markdown(f"""
                            <div class="example-quote">
                                "{example}"
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("---")
    
    # 导出按钮（与 H5包装格式一致）
    st.markdown("### 📥 导出结果")
    col1, col2 = st.columns(2)
    
    with col1:
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 下载 JSON 格式",
            data=json_str,
            file_name=f"analysis_{result.get('group', 'unknown')}_{date}.json",
            mime="application/json"
        )
    
    with col2:
        # 生成完整报告文本（与 H5包装格式一致）
        report_lines = [f"# 玩家社群发言分析报告 - {date}\n\n"]
        report_lines.append(f"## 统计概览\n")
        report_lines.append(f"- 总发言数: {total_messages}\n")
        report_lines.append(f"- 参与玩家数: {total_players}\n")
        report_lines.append(f"- 热门话题簇: {total_clusters}\n\n")
        
        for idx, cluster in enumerate(sorted_clusters[:5], 1):
            report_lines.append(f"## {idx}. {cluster['聚合话题簇']}\n\n")
            report_lines.append(f"- **热度评分**: {cluster['热度评分']}\n")
            report_lines.append(f"- **发言玩家数**: {cluster['发言玩家总数']}\n")
            report_lines.append(f"- **发言总数**: {cluster['发言总数']}\n")
            report_lines.append(f"- **时间轴**: {cluster['时间轴']}\n\n")
            
            # 讨论点列表
            discussion_list = cluster.get('讨论点列表', [])
            if discussion_list:
                report_lines.append(f"### 讨论点与玩家观点\n\n")
                
                for dp in discussion_list:
                    # 获取讨论点标题
                    dp_title = ""
                    for key in dp.keys():
                        if key.startswith("讨论点"):
                            dp_title = dp[key]
                            break
                    
                    if dp_title:
                        report_lines.append(f"#### 📌 {dp_title}\n\n")
                    
                    # 玩家观点
                    opinions = dp.get('玩家观点', [])
                    if opinions:
                        report_lines.append(f"**玩家观点:**\n")
                        for opinion in opinions:
                            report_lines.append(f"- {opinion}\n")
                        report_lines.append("\n")
                    
                    # 代表性玩家发言示例
                    examples = dp.get('代表性玩家发言示例', [])
                    if examples:
                        report_lines.append(f"**代表性发言:**\n")
                        for example in examples:
                            report_lines.append(f'> "{example}"\n')
                        report_lines.append("\n")
                
                report_lines.append("---\n\n")
        
        report_text = "".join(report_lines)
        st.download_button(
            label="📝 下载文本报告",
            data=report_text,
            file_name=f"report_{result.get('group', 'unknown')}_{date}.md",
            mime="text/markdown"
        )


# ==================== 主应用 ====================

def main():
    st.set_page_config(
        page_title="玩家社群分析",
        page_icon="🎮",
        layout="wide",
    )
    
    # 注入 CSS 样式
    st.markdown(STYLE_CSS, unsafe_allow_html=True)
    
    st.title("🎮 玩家社群分析系统")
    st.markdown("查看每日群聊话题分析结果（从 GitHub 自动同步）")
    
    # 侧边栏：选择群和日期
    with st.sidebar:
        st.header("🔍 查询条件")
        
        # 选择群
        group_id = st.radio(
            "选择社群",
            options=list(GROUPS.keys()),
            format_func=lambda x: GROUPS[x]["name"],
            index=0,
        )
        
        st.markdown("---")
        
        # 加载该群的可用日期
        with st.spinner("加载数据列表..."):
            index = load_index(group_id)
            available_dates = index.get("available_dates", [])
        
        if available_dates:
            st.success(f"✅ 共有 {len(available_dates)} 天的数据")
            
            # 选择日期
            selected_date = st.selectbox(
                "选择日期",
                options=available_dates,
                index=0,  # 默认最新
                format_func=lambda x: f"{x} ({'最新' if x == available_dates[0] else ''})".strip(),
            )
        else:
            st.warning("⚠️ 暂无数据")
            selected_date = None
        
        st.markdown("---")
        st.caption("💡 数据每日自动更新到 GitHub")
        
        # 刷新按钮
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # 主内容区
    if selected_date:
        with st.spinner(f"正在加载 {selected_date} 的数据..."):
            result = load_result(group_id, selected_date)
        
        if result:
            render_result(result)
        else:
            st.error(f"❌ 无法加载 {selected_date} 的数据，请检查网络连接或稍后重试")
    else:
        st.info("👈 请在侧边栏选择社群和日期")
        
        # 显示可用数据概览
        st.markdown("### 📊 数据概览")
        
        for gid, group in GROUPS.items():
            with st.spinner(f"加载 {group['name']} 数据..."):
                idx = load_index(gid)
                dates = idx.get("available_dates", [])
            
            if dates:
                st.markdown(f"**{group['name']}**: {len(dates)} 天 (最新: {dates[0]})")
            else:
                st.markdown(f"**{group['name']}**: 暂无数据")


if __name__ == "__main__":
    main()
