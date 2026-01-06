"""
玩家社群分析 - 历史结果查询
Streamlit 应用：查看每日群聊分析结果（从 GitHub 读取）
显示格式与 H5包装保持一致（更稳的 CSS：不做全局 * 强覆盖，只修关键点位）
"""
import streamlit as st
import json
import requests
from datetime import datetime
from pathlib import Path
import time

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

# ==================== CSS（收敛版：稳 + 清晰）===================

STYLE_CSS = """
<style>
:root{
  --primary:#6366f1;
  --secondary:#8b5cf6;
  --accent:#ec4899;
  --bg0:#0f172a;
  --bg1:#1e1b4b;
  --bg2:#312e81;
  --text:#e2e8f0;
  --muted:#94a3b8;
  --line:rgba(99,102,241,.28);
}

/* ===== App 背景 + 基础字体色（不要用 * 全局覆盖）===== */
.stApp{
  background: linear-gradient(135deg, var(--bg0) 0%, var(--bg1) 50%, var(--bg2) 100%);
  color: var(--text);
}

/* 主内容区基础文字 */
section[data-testid="stMain"]{
  color: var(--text);
}
section[data-testid="stMain"] p,
section[data-testid="stMain"] li{
  color: var(--text);
}

/* ===== 标题 ===== */
.main-title{
  font-family: 'Orbitron','Noto Sans SC',sans-serif;
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  text-align:center;
  margin-bottom: .4rem;
  text-shadow: 0 0 28px rgba(129, 140, 248, 0.35);
}
.sub-title{
  font-family: 'Noto Sans SC',sans-serif;
  font-size: 1.05rem;
  color: var(--muted);
  text-align:center;
  margin-bottom: 1.6rem;
}

/* ===== 侧边栏：用稳定选择器，不用 .css-xxxx ===== */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #111b34, #0b1020) !important;
  border-right: 1px solid rgba(148,163,184,.15);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{
  color: #c7d2fe !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] span{
  color: var(--text);
}
section[data-testid="stSidebar"] .stCaption{
  color: var(--muted) !important;
}

/* sidebar 输入框/下拉框：背景变深，边框清晰 */
section[data-testid="stSidebar"] [data-baseweb="select"] > div{
  background: rgba(30,41,59,.92) !important;
  border: 1px solid rgba(148,163,184,.22) !important;
  border-radius: 12px !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"]{
  background: rgba(30,41,59,.92) !important;
  border: 1px solid rgba(148,163,184,.22) !important;
  border-radius: 12px !important;
}
section[data-testid="stSidebar"] input{
  color: var(--text) !important;
}

/* 下拉菜单弹层（options） */
div[data-baseweb="menu"]{
  background: rgba(15,23,42,.98) !important;
  border: 1px solid rgba(148,163,184,.20) !important;
  border-radius: 12px !important;
}
div[data-baseweb="option"]{
  color: var(--text) !important;
}
div[data-baseweb="option"]:hover{
  background: rgba(99,102,241,.18) !important;
}

/* ===== 日期选择器年份下拉菜单优化 ===== */
/* 确保年份选择器可以正常显示和选择 */
section[data-testid="stSidebar"] div[data-baseweb="select"] select,
section[data-testid="stSidebar"] div[role="combobox"] input{
  color: var(--text) !important;
}
/* 日期选择器的年份下拉菜单 */
div[data-baseweb="popover"]{
  background: rgba(15,23,42,.98) !important;
  border: 1px solid rgba(148,163,184,.20) !important;
  border-radius: 12px !important;
  z-index: 9999 !important;
}
/* 确保年份选择下拉菜单可见且可点击 */
div[data-baseweb="popover"] div[role="listbox"],
div[data-baseweb="popover"] div[role="option"]{
  color: var(--text) !important;
  background: rgba(15,23,42,.98) !important;
}
div[data-baseweb="popover"] div[role="option"]:hover{
  background: rgba(99,102,241,.18) !important;
}

/* ===== 日期选择器：禁用不可用日期 ===== */
/* 日历中不在可用日期范围内的日期会被 Streamlit 自动禁用（灰色显示） */
section[data-testid="stSidebar"] input[type="date"]{
  color: var(--text) !important;
}
/* 日历弹窗样式 */
div[data-baseweb="popover"] table,
div[data-baseweb="popover"] td,
div[data-baseweb="popover"] th{
  color: var(--text) !important;
}
/* 禁用的日期（灰色，不可点击）- 通过 JavaScript 添加的样式 */
div[data-baseweb="popover"] button[disabled],
div[data-baseweb="popover"] button[aria-disabled="true"],
div[data-baseweb="popover"] button.date-disabled{
  opacity: 0.4 !important;
  cursor: not-allowed !important;
  pointer-events: none !important;
  color: var(--muted) !important;
  background: rgba(148,163,184,.1) !important;
  user-select: none !important;
}
/* 禁用日期的禁止符号样式 */
div[data-baseweb="popover"] button.date-disabled .date-disabled-icon {
  display: inline-block !important;
  font-size: 10px !important;
  margin-left: 2px !important;
  vertical-align: middle !important;
  opacity: 0.8 !important;
}
/* 可用的日期（正常显示，可点击） */
div[data-baseweb="popover"] button:not([disabled]):not([aria-disabled="true"]):not(.date-disabled){
  cursor: pointer !important;
  opacity: 1 !important;
}
div[data-baseweb="popover"] button:not([disabled]):not([aria-disabled="true"]):not(.date-disabled):hover{
  background: rgba(99,102,241,.18) !important;
}

/* ===== 按钮 ===== */
.stButton > button{
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  color: #fff !important;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1.2rem;
  font-weight: 700;
  transition: all .25s ease;
  box-shadow: 0 6px 18px rgba(99,102,241,.35);
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 10px 26px rgba(99,102,241,.45);
}

/* ===== 统计概览卡 ===== */
.stats-overview{
  background: linear-gradient(145deg, rgba(30,41,59,.95), rgba(51,65,85,.92));
  border-radius: 18px;
  padding: 1.6rem;
  margin: 1.2rem 0 1.4rem 0;
  border: 1px solid var(--line);
  box-shadow: 0 10px 26px rgba(0,0,0,.25);
}
.stats-overview h2{
  color: #c7d2fe;
  margin: 0 0 1rem 0;
  padding-bottom: .6rem;
  border-bottom: 1px solid rgba(199,210,254,.25);
}
.stat-grid{
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.stat-item{
  background: rgba(99,102,241,.10);
  border: 1px solid rgba(99,102,241,.18);
  border-radius: 14px;
  padding: 1rem;
  text-align:center;
}
.stat-value{
  font-size: 1.9rem;
  font-weight: 800;
  color: #c7d2fe;
}
.stat-label{
  font-size: .9rem;
  color: var(--muted);
}

/* ===== 关键修复：Expander 标题条/内容 ===== */
section[data-testid="stMain"] div[data-testid="stExpander"] details > summary{
  background: rgba(15,23,42,.88) !important;
  border: 1px solid rgba(148,163,184,.18) !important;
  border-radius: 14px !important;
  padding: 12px 16px !important;
}
section[data-testid="stMain"] div[data-testid="stExpander"] details > summary *{
  color: var(--text) !important;
  font-weight: 700 !important;
}
section[data-testid="stMain"] div[data-testid="stExpander"] div[role="region"]{
  background: rgba(30,41,59,.35) !important;
  border: 1px solid rgba(148,163,184,.12) !important;
  border-radius: 14px !important;
  padding: 10px 12px !important;
}

/* Metric */
[data-testid="stMetricValue"]{ color: #c7d2fe !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"]{ color: var(--muted) !important; }

/* ===== 讨论点 / 观点 / 引用块 ===== */
.discussion-point{
  background: rgba(236,72,153,.14);
  border-left: 4px solid var(--accent);
  padding: .9rem 1rem;
  margin: .8rem 0;
  border-radius: 0 10px 10px 0;
}
.discussion-point strong{
  color:#fff;
  font-size: 1.05rem;
}
.opinion-item{
  background: rgba(34,211,238,.12);
  border: 1px solid rgba(34,211,238,.18);
  padding: .8rem 1rem;
  margin: .55rem 0;
  border-radius: 10px;
  color: var(--text);
}
.example-quote{
  background: rgba(99,102,241,.10);
  border-left: 3px solid rgba(99,102,241,.9);
  padding: .7rem .9rem;
  margin: .45rem 0;
  border-radius: 10px;
  color: #d7e0ef;
  font-style: italic;
}

/* 链接颜色 */
a{ color:#a5b4fc !important; }
</style>
"""


# ==================== 网络读取（带刷新 nonce 防缓存）===================

def _get_nonce() -> str:
    # 用于 “刷新数据” 时强制拉新
    return st.session_state.get("_nonce", "")

def _set_nonce():
    st.session_state["_nonce"] = str(int(time.time()))

def fetch_json(url: str) -> dict | None:
    """
    读取远端 json
    - 加 nonce query param，配合 refresh 按钮可强制绕过缓存
    - requests.get + timeout
    """
    nonce = _get_nonce()
    if nonce:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}v={nonce}"

    r = requests.get(url, timeout=10, headers={"Cache-Control": "no-cache"})
    if r.status_code == 200:
        return r.json()
    return None


# ==================== 数据加载 ====================

@st.cache_data(ttl=300, show_spinner=False)
def load_index(group_id: str) -> dict:
    group = GROUPS.get(group_id)
    if not group:
        return {}

    # 本地优先
    local_path = LOCAL_RESULTS_DIR / group["dir"] / "index.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 远端
    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/index.json"
        data = fetch_json(url)
        return data or {}
    except Exception as e:
        st.error(f"加载索引失败: {e}")
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def load_result(group_id: str, date: str) -> dict:
    group = GROUPS.get(group_id)
    if not group:
        return {}

    # 本地优先
    local_path = LOCAL_RESULTS_DIR / group["dir"] / f"{date}.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 远端
    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/{date}.json"
        data = fetch_json(url)
        return data or {}
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return {}


# ==================== 渲染 ====================

def render_result(result: dict):
    if not result:
        st.warning("⚠️ 暂无数据")
        return

    date = result.get("date", "")
    clusters = result.get("clusters", [])
    summary = result.get("summary", {})

    total_clusters = summary.get("total_clusters", len(clusters))
    total_players = summary.get("total_players", 0)
    total_messages = summary.get("total_messages", 0)

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🔥 热门话题 Top 5")

    sorted_clusters = sorted(clusters, key=lambda x: x.get("热度评分", 0), reverse=True)

    for idx, cluster in enumerate(sorted_clusters[:5], 1):
        with st.expander(f"#{idx} {cluster.get('聚合话题簇','(未命名话题)')}", expanded=(idx <= 2)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("热度评分", f"{float(cluster.get('热度评分', 0)):.1f} 🔥")
            with col2:
                st.metric("发言玩家数", cluster.get("发言玩家总数", 0))
            with col3:
                st.metric("发言总数", cluster.get("发言总数", 0))

            st.markdown(f"**⏰ 时间轴:** {cluster.get('时间轴','')}")

            discussion_list = cluster.get("讨论点列表", [])
            if discussion_list:
                st.markdown("#### 💬 讨论点与玩家观点")

                for dp in discussion_list:
                    # 讨论点标题
                    dp_title = ""
                    for k in dp.keys():
                        if str(k).startswith("讨论点"):
                            dp_title = dp.get(k, "")
                            break

                    if dp_title:
                        st.markdown(
                            f"""
                            <div class="discussion-point">
                                <strong>📌 {dp_title}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    opinions = dp.get("玩家观点", [])
                    if opinions:
                        st.markdown("**玩家观点:**")
                        for opinion in opinions:
                            st.markdown(
                                f"""
                                <div class="opinion-item">
                                    {opinion}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    examples = dp.get("代表性玩家发言示例", [])
                    if examples:
                        st.markdown("**代表性发言:**")
                        for example in examples:
                            st.markdown(
                                f"""
                                <div class="example-quote">
                                    "{example}"
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    st.markdown("---")

    # 导出
    st.markdown("### 📥 导出结果")
    col1, col2 = st.columns(2)

    with col1:
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 下载 JSON 格式",
            data=json_str,
            file_name=f"analysis_{result.get('group', 'unknown')}_{date}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        report_lines = [f"# 玩家社群发言分析报告 - {date}\n\n"]
        report_lines.append("## 统计概览\n")
        report_lines.append(f"- 总发言数: {total_messages}\n")
        report_lines.append(f"- 参与玩家数: {total_players}\n")
        report_lines.append(f"- 热门话题簇: {total_clusters}\n\n")

        for idx, cluster in enumerate(sorted_clusters[:5], 1):
            report_lines.append(f"## {idx}. {cluster.get('聚合话题簇','(未命名话题)')}\n\n")
            report_lines.append(f"- **热度评分**: {cluster.get('热度评分', 0)}\n")
            report_lines.append(f"- **发言玩家数**: {cluster.get('发言玩家总数', 0)}\n")
            report_lines.append(f"- **发言总数**: {cluster.get('发言总数', 0)}\n")
            report_lines.append(f"- **时间轴**: {cluster.get('时间轴','')}\n\n")

            discussion_list = cluster.get("讨论点列表", [])
            if discussion_list:
                report_lines.append("### 讨论点与玩家观点\n\n")

                for dp in discussion_list:
                    dp_title = ""
                    for k in dp.keys():
                        if str(k).startswith("讨论点"):
                            dp_title = dp.get(k, "")
                            break
                    if dp_title:
                        report_lines.append(f"#### 📌 {dp_title}\n\n")

                    opinions = dp.get("玩家观点", [])
                    if opinions:
                        report_lines.append("**玩家观点:**\n")
                        for opinion in opinions:
                            report_lines.append(f"- {opinion}\n")
                        report_lines.append("\n")

                    examples = dp.get("代表性玩家发言示例", [])
                    if examples:
                        report_lines.append("**代表性发言:**\n")
                        for example in examples:
                            report_lines.append(f'> "{example}"\n')
                        report_lines.append("\n")

                report_lines.append("---\n\n")

        report_text = "".join(report_lines)
        st.download_button(
            label="📝 下载文本报告",
            data=report_text,
            file_name=f"report_{result.get('group', 'unknown')}_{date}.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ==================== 主应用 ====================

def main():
    st.set_page_config(
        page_title="玩家社群分析",
        page_icon="🎮",
        layout="wide",
        # 如果你不想窄屏出现“侧边栏蒙版”，建议默认收起：
        initial_sidebar_state="collapsed",
    )

    # 注入 CSS
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
                sorted_date_objects = sorted(date_objects, reverse=True)
                default_date = sorted_date_objects[0]
                min_date = min(date_objects)
                max_date = max(date_objects)
                
                # 设置日期范围为实际可用日期的范围（而不是整年）
                # 这样 Streamlit 会自动禁用范围外的日期
                # 但范围内的不可用日期需要通过 JavaScript 禁用
                from datetime import date as date_type
                min_year = min_date.year
                max_year = max_date.year
                extended_min_date = date_type(min_year, 1, 1)
                extended_max_date = date_type(max_year, 12, 31)
                
                # 使用 session_state 来存储上次选择的日期，避免无效选择
                if 'selected_date_cache' not in st.session_state:
                    st.session_state.selected_date_cache = default_date.strftime("%Y-%m-%d")
                
                # 从缓存中恢复上次选择的日期（如果存在）
                try:
                    cached_date_obj = datetime.strptime(st.session_state.selected_date_cache, "%Y-%m-%d").date()
                    if cached_date_obj in date_objects:
                        initial_date = cached_date_obj
                    else:
                        initial_date = default_date
                except:
                    initial_date = default_date
                
                # 定义日期变化回调函数，快速验证并响应
                def on_date_change():
                    # 从 session_state 获取当前选择的日期对象
                    selected_date_obj_check = st.session_state.get('selected_date_input', initial_date)
                    if isinstance(selected_date_obj_check, str):
                        try:
                            selected_date_obj_check = datetime.strptime(selected_date_obj_check, "%Y-%m-%d").date()
                        except:
                            selected_date_obj_check = initial_date
                    
                    selected_date_str_check = selected_date_obj_check.strftime("%Y-%m-%d")
                    
                    if selected_date_str_check not in available_dates:
                        # 快速找到最近的可用日期
                        selected_date_obj_dt = datetime.combine(selected_date_obj_check, datetime.min.time())
                        closest_date = min(
                            date_objects,
                            key=lambda x: abs((datetime.combine(x, datetime.min.time()) - selected_date_obj_dt).days)
                        )
                        closest_date_str = closest_date.strftime("%Y-%m-%d")
                        st.session_state.selected_date_cache = closest_date_str
                        st.session_state.selected_date_input = closest_date
                        # 格式化日期显示（中文格式）
                        formatted_date = selected_date_obj_check.strftime("%Y年%m月%d日")
                        st.markdown(
                            f'<div style="padding: 1rem; background-color: rgba(255, 193, 7, 0.1); '
                            f'border-left: 4px solid #ffc107; border-radius: 4px; margin: 1rem 0;">'
                            f'<p style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #ffc107;">'
                            f'⚠️ {formatted_date}暂无数据</p></div>',
                            unsafe_allow_html=True
                        )
                        st.rerun()
                    else:
                        st.session_state.selected_date_cache = selected_date_str_check
                
                selected_date_obj = st.date_input(
                    "选择日期",
                    value=initial_date,
                    min_value=extended_min_date,
                    max_value=extended_max_date,
                    help="只能选择已上传到数据库的日期（带禁止符号的日期不可选）",
                    key='selected_date_input',
                    on_change=on_date_change
                )
                
                # 注入 JavaScript 来禁用不在 available_dates 中的日期
                # 将可用日期列表转换为 JavaScript 数组
                available_dates_js = json.dumps(available_dates)
                disable_dates_js = f"""
                <script>
                (function() {{
                    const availableDates = {available_dates_js};
                    console.log('可用日期列表:', availableDates);
                    
                    function disableUnavailableDates() {{
                        // 查找日历弹窗
                        const popover = document.querySelector('div[data-baseweb="popover"]');
                        if (!popover) {{
                            console.log('未找到日历弹窗');
                            return;
                        }}
                        
                        // 查找日历表格
                        const table = popover.querySelector('table');
                        if (!table) {{
                            console.log('未找到日历表格');
                            return;
                        }}
                        
                        // 获取当前显示的月份和年份 - 使用更可靠的方法
                        let currentYear = null;
                        let currentMonth = null;
                        
                        // 方法1: 从日历标题按钮获取
                        const headerButtons = popover.querySelectorAll('button[role="combobox"]');
                        headerButtons.forEach(btn => {{
                            const text = (btn.textContent || btn.getAttribute('aria-label') || '').trim();
                            console.log('日历标题按钮文本:', text);
                            
                            // 提取年份
                            const yearMatch = text.match(/(\\d{{4}})/);
                            if (yearMatch) {{
                                currentYear = parseInt(yearMatch[1]);
                                console.log('找到年份:', currentYear);
                            }}
                            
                            // 提取月份
                            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                                               'July', 'August', 'September', 'October', 'November', 'December'];
                            const monthNamesCN = ['一月', '二月', '三月', '四月', '五月', '六月',
                                                 '七月', '八月', '九月', '十月', '十一月', '十二月'];
                            
                            for (let i = 0; i < monthNames.length; i++) {{
                                if (text.toLowerCase().includes(monthNames[i].toLowerCase()) ||
                                    text.includes(monthNamesCN[i])) {{
                                    currentMonth = i;
                                    console.log('找到月份:', monthNames[i], i);
                                    break;
                                }}
                            }}
                        }});
                        
                        // 方法2: 如果还没找到，从输入框的值获取
                        if (currentYear === null || currentMonth === null) {{
                            const dateInput = document.querySelector('input[type="date"]');
                            if (dateInput && dateInput.value) {{
                                const inputDate = new Date(dateInput.value);
                                currentYear = currentYear || inputDate.getFullYear();
                                currentMonth = currentMonth !== null ? currentMonth : inputDate.getMonth();
                                console.log('从输入框获取:', currentYear, currentMonth);
                            }}
                        }}
                        
                        // 方法3: 如果还是没找到，使用当前日期
                        if (currentYear === null || currentMonth === null) {{
                            const now = new Date();
                            currentYear = currentYear || now.getFullYear();
                            currentMonth = currentMonth !== null ? currentMonth : now.getMonth();
                            console.log('使用当前日期:', currentYear, currentMonth);
                        }}
                        
                        console.log('最终年月:', currentYear, currentMonth);
                        
                        // 查找所有日期按钮（在表格的 tbody 中）
                        const tbody = table.querySelector('tbody');
                        if (!tbody) {{
                            console.log('未找到 tbody');
                            return;
                        }}
                        
                        const dateButtons = tbody.querySelectorAll('button');
                        console.log('找到日期按钮数量:', dateButtons.length);
                        
                        let disabledCount = 0;
                        let enabledCount = 0;
                        
                        dateButtons.forEach(button => {{
                            // 获取按钮的原始文本（去除可能已添加的禁止符号）
                            let dayText = button.textContent.trim();
                            // 移除可能存在的禁止符号和空格
                            dayText = dayText.replace(/🚫/g, '').replace(/\s+/g, '').trim();
                            
                            // 如果按钮有保存的原始文本，使用它
                            if (button.dataset.originalText) {{
                                dayText = button.dataset.originalText;
                            }}
                            
                            const day = parseInt(dayText);
                            
                            // 跳过非数字内容（可能是月份导航按钮等）
                            if (isNaN(day) || day < 1 || day > 31) return;
                            
                            // 构建日期字符串 YYYY-MM-DD
                            const dateStr = `${{currentYear}}-${{String(currentMonth + 1).padStart(2, '0')}}-${{String(day).padStart(2, '0')}}`;
                            
                            // 检查日期是否在可用列表中
                            if (!availableDates.includes(dateStr)) {{
                                // 保存原始文本（如果还没有）
                                if (!button.dataset.originalText) {{
                                    button.dataset.originalText = dayText;
                                }}
                                
                                // 禁用该日期按钮
                                button.disabled = true;
                                button.setAttribute('aria-disabled', 'true');
                                button.style.opacity = '0.4';
                                button.style.cursor = 'not-allowed';
                                button.style.pointerEvents = 'none';
                                button.style.userSelect = 'none';
                                button.classList.add('date-disabled');
                                
                                // 添加禁止符号（强制更新）
                                const existingIcon = button.querySelector('.date-disabled-icon');
                                if (existingIcon) {{
                                    existingIcon.remove();
                                }}
                                const icon = document.createElement('span');
                                icon.className = 'date-disabled-icon';
                                icon.textContent = '🚫';
                                icon.style.cssText = 'font-size: 12px; margin-left: 3px; vertical-align: middle; display: inline-block;';
                                // 在日期数字后添加禁止符号
                                button.innerHTML = button.dataset.originalText + ' ' + icon.outerHTML;
                                
                                // 移除所有现有的事件监听器（通过克隆并替换）
                                const oldButton = button;
                                const newButton = oldButton.cloneNode(true);
                                oldButton.parentNode.replaceChild(newButton, oldButton);
                                
                                // 添加阻止点击事件（使用捕获阶段，优先级最高）
                                newButton.addEventListener('click', function(e) {{
                                    e.preventDefault();
                                    e.stopPropagation();
                                    e.stopImmediatePropagation();
                                    console.log('阻止点击不可用日期:', dateStr);
                                    return false;
                                }}, true);
                                
                                newButton.addEventListener('mousedown', function(e) {{
                                    e.preventDefault();
                                    e.stopPropagation();
                                    e.stopImmediatePropagation();
                                    return false;
                                }}, true);
                                
                                newButton.addEventListener('mouseup', function(e) {{
                                    e.preventDefault();
                                    e.stopPropagation();
                                    e.stopImmediatePropagation();
                                    return false;
                                }}, true);
                                
                                disabledCount++;
                            }} else {{
                                // 确保可用日期是可点击的
                                button.disabled = false;
                                button.removeAttribute('aria-disabled');
                                button.style.opacity = '1';
                                button.style.cursor = 'pointer';
                                button.style.pointerEvents = 'auto';
                                button.style.userSelect = 'auto';
                                button.classList.remove('date-disabled');
                                
                                // 移除禁止符号（如果存在）
                                const icon = button.querySelector('.date-disabled-icon');
                                if (icon) {{
                                    icon.remove();
                                }}
                                // 恢复原始文本
                                if (button.dataset.originalText) {{
                                    button.textContent = button.dataset.originalText;
                                    delete button.dataset.originalText;
                                }}
                                
                                enabledCount++;
                            }}
                        }});
                        
                        console.log(`已禁用 ${{disabledCount}} 个日期，启用 ${{enabledCount}} 个日期`);
                    }}
                    
                    // 使用 MutationObserver 监听日历弹窗的出现和变化
                    const observer = new MutationObserver(function(mutations) {{
                        const hasPopover = document.querySelector('div[data-baseweb="popover"]');
                        if (hasPopover) {{
                            disableUnavailableDates();
                        }}
                    }});
                    
                    // 开始观察整个文档
                    observer.observe(document.body, {{
                        childList: true,
                        subtree: true,
                        attributes: true,
                        attributeFilter: ['aria-expanded', 'aria-hidden', 'style']
                    }});
                    
                    // 监听点击事件，当日期选择器打开时执行
                    document.addEventListener('click', function(e) {{
                        const target = e.target;
                        if (target.closest('[data-baseweb="popover"]') || 
                            target.closest('input[type="date"]') ||
                            target.closest('button[aria-label*="date"]') ||
                            target.closest('button[role="combobox"]')) {{
                            setTimeout(disableUnavailableDates, 50);
                            setTimeout(disableUnavailableDates, 200);
                            setTimeout(disableUnavailableDates, 500);
                        }}
                        
                        // 拦截不可用日期的点击
                        if (target.classList.contains('date-disabled') || 
                            target.closest('.date-disabled')) {{
                            e.preventDefault();
                            e.stopPropagation();
                            e.stopImmediatePropagation();
                            return false;
                        }}
                    }}, true);
                    
                    // 额外的事件拦截器：在捕获阶段阻止不可用日期的点击
                    document.addEventListener('mousedown', function(e) {{
                        const target = e.target;
                        if (target.classList.contains('date-disabled') || 
                            target.closest('.date-disabled')) {{
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }}
                    }}, true);
                    
                    // 监听输入框焦点事件
                    document.addEventListener('focusin', function(e) {{
                        if (e.target.tagName === 'INPUT' && e.target.type === 'date') {{
                            setTimeout(disableUnavailableDates, 100);
                            setTimeout(disableUnavailableDates, 300);
                        }}
                    }}, true);
                    
                    // 立即执行几次（延迟执行以确保日历已渲染）
                    setTimeout(disableUnavailableDates, 50);
                    setTimeout(disableUnavailableDates, 100);
                    setTimeout(disableUnavailableDates, 300);
                    setTimeout(disableUnavailableDates, 500);
                    setTimeout(disableUnavailableDates, 1000);
                    setTimeout(disableUnavailableDates, 2000);
                    
                    // 定期检查（防止日历更新后失效）
                    setInterval(function() {{
                        const popover = document.querySelector('div[data-baseweb="popover"]');
                        if (popover && popover.style.display !== 'none') {{
                            disableUnavailableDates();
                        }}
                    }}, 500);
                }})();
                </script>
                """
                st.markdown(disable_dates_js, unsafe_allow_html=True)
                
                # 转换为字符串格式
                # 注意：日期验证已在 on_change 回调中处理，这里只需要确保缓存是最新的
                selected_date = selected_date_obj.strftime("%Y-%m-%d")
                
                # 确保缓存是最新的（on_change 回调已经处理了验证和警告）
                if selected_date in available_dates:
                    st.session_state.selected_date_cache = selected_date
            else:
                selected_date = None
        else:
            st.warning("⚠️ 暂无数据")
            selected_date = None
        
        st.markdown("---")
        st.caption("💡 数据每日自动更新到 GitHub")
        
        # 刷新按钮
        if st.button("🔄 刷新数据", use_container_width=True):
            # 清除所有缓存
            st.cache_data.clear()
            # 更新 nonce 强制刷新
            _set_nonce()
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
