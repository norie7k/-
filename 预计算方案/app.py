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

# ==================== CSS 样式（参考 H5包装配色）===================

STYLE_CSS = """
<style>
    /* 主题颜色 */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #ec4899;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* 全局背景 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        color: #e2e8f0;
    }
    
    /* 标题样式 */
    .main-title {
        font-family: 'Orbitron', 'Noto Sans SC', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(129, 140, 248, 0.5);
    }
    
    .sub-title {
        font-family: 'Noto Sans SC', sans-serif;
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 统计概览 */
    .stats-overview {
        background: linear-gradient(145deg, #312e81, #3730a3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        color: #e2e8f0;
    }
    
    .stats-overview h2 {
        color: #c7d2fe;
        margin-bottom: 1rem;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        color: #e2e8f0;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #818cf8;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }
    
    /* 讨论点样式 */
    .discussion-point {
        background: rgba(236, 72, 153, 0.1);
        border-left: 4px solid #ec4899;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 0 8px 8px 0;
        color: #e2e8f0;
    }
    
    .discussion-point strong {
        color: #f1f5f9;
    }
    
    .opinion-item {
        background: rgba(34, 211, 238, 0.08);
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        color: #e2e8f0;
    }
    
    .example-quote {
        font-style: italic;
        color: #94a3b8;
        padding: 0.5rem;
        border-left: 3px solid #6366f1;
        margin: 0.3rem 0;
        background: rgba(99, 102, 241, 0.05);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b, #0f172a);
    }
    
    /* 侧边栏所有文字 - 确保清晰可见 */
    section[data-testid="stSidebar"] {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #a5b4fc !important;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    /* 侧边栏 Selectbox 和 Date Input */
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: #e2e8f0 !important;
    }
    
    /* 侧边栏输入框/下拉框：背景变深，文字清晰 */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(30, 41, 59, 0.92) !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="select"] > div > div {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="input"] {
        background: rgba(30, 41, 59, 0.92) !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 12px !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="input"] input {
        color: #e2e8f0 !important;
    }
    
    /* 下拉菜单弹层（options）- 全局样式，包括侧边栏 */
    div[data-baseweb="menu"] {
        background: rgba(15, 23, 42, 0.98) !important;
        border: 1px solid rgba(148, 163, 184, 0.20) !important;
        border-radius: 12px !important;
    }
    
    div[data-baseweb="option"] {
        color: #e2e8f0 !important;
    }
    
    div[data-baseweb="option"]:hover {
        background: rgba(99, 102, 241, 0.18) !important;
    }
    
    /* 侧边栏 Markdown */
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown * {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown strong {
        color: #f1f5f9 !important;
    }
    
    /* 侧边栏 Caption */
    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }
    
    /* 侧边栏 Success/Warning/Info */
    section[data-testid="stSidebar"] .stSuccess,
    section[data-testid="stSidebar"] .stWarning,
    section[data-testid="stSidebar"] .stInfo {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .stSuccess *,
    section[data-testid="stSidebar"] .stWarning *,
    section[data-testid="stSidebar"] .stInfo * {
        color: #e2e8f0 !important;
    }
    
    /* 侧边栏 Baseweb 组件（Streamlit 使用的 UI 库） */
    section[data-testid="stSidebar"] [data-baseweb="select"] {
        color: #e2e8f0 !important;
        background-color: #1e293b !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="input"] {
        color: #e2e8f0 !important;
        background-color: #1e293b !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="input"] input {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="calendar"] {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="calendar"] * {
        color: #e2e8f0 !important;
    }
    
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.6);
    }
    
    /* 卡片样式 */
    .result-card {
        background: linear-gradient(145deg, #1e293b, #334155);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        color: #e2e8f0;
    }
    
    /* 主内容区域文字 */
    section[data-testid="stMain"] {
        color: #e2e8f0;
    }
    
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] div,
    section[data-testid="stMain"] span {
        color: #e2e8f0;
    }
    
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3,
    section[data-testid="stMain"] h4,
    section[data-testid="stMain"] h5,
    section[data-testid="stMain"] h6 {
        color: #a5b4fc;
    }
    
    /* Expander 内容 */
    .streamlit-expanderHeader {
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderContent {
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderContent p,
    .streamlit-expanderContent div {
        color: #e2e8f0 !important;
    }
    
    /* Metric 组件 */
    [data-testid="stMetricValue"] {
        color: #818cf8 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Markdown 文字 */
    .stMarkdown {
        color: #e2e8f0;
    }
    
    .stMarkdown p {
        color: #e2e8f0;
    }
    
    .stMarkdown strong {
        color: #a5b4fc;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1, #ec4899);
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
        initial_sidebar_state="expanded"
    )
    
    # 注入 CSS 样式
    st.markdown(STYLE_CSS, unsafe_allow_html=True)
    
    # 标题（与 H5包装一致）
    st.markdown("""
    <div class="main-title">🎮 玩家社群分析系统</div>
    <div class="sub-title">查看每日群聊话题分析结果（从 GitHub 自动同步）</div>
    """, unsafe_allow_html=True)
    
    # 侧边栏：选择群和日期
    with st.sidebar:
        st.header("🔍 查询条件")
        
        # 选择群（下拉菜单）
        group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
        selected_group_key = st.selectbox(
            "选择社群",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            index=0,
        )
        
        st.markdown("---")
        
        # 加载该群的可用日期
        with st.spinner("加载数据列表..."):
            index = load_index(selected_group_key)
            available_dates = index.get("available_dates", [])
        
        if available_dates:
            st.success(f"✅ 共有 {len(available_dates)} 天的数据")
            
            # 日期选择（日历组件）
            # 将字符串日期转换为 date 对象
            date_objects = []
            for date_str in available_dates:
                try:
                    date_objects.append(datetime.strptime(date_str, "%Y-%m-%d").date())
                except:
                    pass
            
            if date_objects:
                # 默认选择最新日期
                default_date = date_objects[0]
                min_date = min(date_objects)
                max_date = max(date_objects)
                
                selected_date_obj = st.date_input(
                    "选择日期",
                    value=default_date,
                    min_value=min_date,
                    max_value=max_date,
                    help="选择要查看的分析日期"
                )
                
                # 转换为字符串格式
                selected_date = selected_date_obj.strftime("%Y-%m-%d")
                
                # 检查选择的日期是否在可用列表中
                if selected_date not in available_dates:
                    st.warning(f"⚠️ {selected_date} 暂无数据，已自动选择最新日期")
                    selected_date = available_dates[0]
            else:
                selected_date = None
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
            result = load_result(selected_group_key, selected_date)
        
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
