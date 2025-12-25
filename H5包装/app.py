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

# ==================== 配置 ====================

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/norie7k/-/main/预计算方案/results"
LOCAL_RESULTS_DIR = Path(__file__).parent / "results"

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
  --card:#1e293b;
  --card2:#334155;
  --text:#e2e8f0;
  --muted:#94a3b8;
  --title:#a5b4fc;
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

/* ===== 关键修复：Expander 标题条看不清 ===== */
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

# ==================== 数据加载 ====================

@st.cache_data(ttl=300)
def load_index(group_id: str) -> dict:
    group = GROUPS.get(group_id)
    if not group:
        return {}

    local_path = LOCAL_RESULTS_DIR / group["dir"] / "index.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/index.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"加载索引失败: {e}")

    return {}

@st.cache_data(ttl=300)
def load_result(group_id: str, date: str) -> dict:
    group = GROUPS.get(group_id)
    if not group:
        return {}

    local_path = LOCAL_RESULTS_DIR / group["dir"] / f"{date}.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/{date}.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
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

    st.markdown("### 🔥 热门话题 Top 5")

    sorted_clusters = sorted(clusters, key=lambda x: x.get("热度评分", 0), reverse=True)

    for idx, cluster in enumerate(sorted_clusters[:5], 1):
        with st.expander(f"#{idx} {cluster['聚合话题簇']}", expanded=(idx <= 2)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("热度评分", f"{cluster['热度评分']:.1f} 🔥")
            with col2:
                st.metric("发言玩家数", cluster["发言玩家总数"])
            with col3:
                st.metric("发言总数", cluster["发言总数"])

            st.markdown(f"**⏰ 时间轴:** {cluster['时间轴']}")

            discussion_list = cluster.get("讨论点列表", [])
            if discussion_list:
                st.markdown("#### 💬 讨论点与玩家观点")

                for dp in discussion_list:
                    dp_title = ""
                    for k in dp.keys():
                        if k.startswith("讨论点"):
                            dp_title = dp[k]
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

    st.markdown("### 📥 导出结果")
    col1, col2 = st.columns(2)

    with col1:
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 下载 JSON 格式",
            data=json_str,
            file_name=f"analysis_{result.get('group', 'unknown')}_{date}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        report_lines = [f"# 玩家社群发言分析报告 - {date}\n\n"]
        report_lines.append("## 统计概览\n")
        report_lines.append(f"- 总发言数: {total_messages}\n")
        report_lines.append(f"- 参与玩家数: {total_players}\n")
        report_lines.append(f"- 热门话题簇: {total_clusters}\n\n")

        for idx, cluster in enumerate(sorted_clusters[:5], 1):
            report_lines.append(f"## {idx}. {cluster['聚合话题簇']}\n\n")
            report_lines.append(f"- **热度评分**: {cluster['热度评分']}\n")
            report_lines.append(f"- **发言玩家数**: {cluster['发言玩家总数']}\n")
            report_lines.append(f"- **发言总数**: {cluster['发言总数']}\n")
            report_lines.append(f"- **时间轴**: {cluster['时间轴']}\n\n")

            discussion_list = cluster.get("讨论点列表", [])
            if discussion_list:
                report_lines.append("### 讨论点与玩家观点\n\n")

                for dp in discussion_list:
                    dp_title = ""
                    for k in dp.keys():
                        if k.startswith("讨论点"):
                            dp_title = dp[k]
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
            use_container_width=True
        )

# ==================== 主应用 ====================

def main():
    st.set_page_config(
        page_title="玩家社群分析",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(STYLE_CSS, unsafe_allow_html=True)
    st.markdown(
        "<div style='position:fixed;bottom:12px;right:12px;background:#ff0000;color:#fff;padding:8px 10px;border-radius:8px;z-index:99999;'>BUILD: V1</div>",
        unsafe_allow_html=True
    )
    st.markdown("""
    <div class="main-title">🎮 玩家社群分析系统</div>
    <div class="sub-title">查看每日群聊话题分析结果（从 GitHub 自动同步）</div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔍 查询条件")

        group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
        selected_group_key = st.selectbox(
            "选择社群",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            index=0,
        )

        st.markdown("---")

        with st.spinner("加载数据列表..."):
            index = load_index(selected_group_key)
            available_dates = index.get("available_dates", [])

        if available_dates:
            st.success(f"✅ 共有 {len(available_dates)} 天的数据")

            date_objects = []
            for d in available_dates:
                try:
                    date_objects.append(datetime.strptime(d, "%Y-%m-%d").date())
                except Exception:
                    pass

            if date_objects:
                default_date = date_objects[0]
                min_date = min(date_objects)
                max_date = max(date_objects)

                selected_date_obj = st.date_input(
                    "选择日期",
                    value=default_date,
                    min_value=min_date,
                    max_value=max_date,
                    help="选择要查看的分析日期",
                )
                selected_date = selected_date_obj.strftime("%Y-%m-%d")

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

        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if selected_date:
        with st.spinner(f"正在加载 {selected_date} 的数据..."):
            result = load_result(selected_group_key, selected_date)

        if result:
            render_result(result)
        else:
            st.error(f"❌ 无法加载 {selected_date} 的数据，请检查网络连接或稍后重试")
    else:
        st.info("👈 请在侧边栏选择社群和日期")

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
