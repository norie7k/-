"""
玩家社群分析 - 历史结果查询
Streamlit 应用：查看每日群聊分析结果（从 GitHub 读取）
展示：摘要卡 + 展开详情（讨论点/观点/代表发言）
不需要左侧目录
"""

import streamlit as st
import streamlit.components.v1 as components
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

  --bg0:#0b1020;
  --bg1:#111b34;
  --bg2:#1e1b4b;

  --card:#121a31;
  --card2:#0f172a;
  --line:rgba(148,163,184,.18);

  --text:#e5e7eb;
  --muted:#94a3b8;
  --muted2:#64748b;
}

/* ===== App 背景 + 基础字体色 ===== */
.stApp{
  background: radial-gradient(1200px 800px at 20% 0%, rgba(99,102,241,.20), transparent 60%),
              radial-gradient(1000px 700px at 85% 30%, rgba(236,72,153,.14), transparent 55%),
              linear-gradient(135deg, var(--bg0) 0%, var(--bg1) 45%, var(--bg2) 100%);
  color: var(--text);
}

/* 主内容区基础文字 */
section[data-testid="stMain"]{ color: var(--text); }
section[data-testid="stMain"] p,
section[data-testid="stMain"] li{ color: var(--text); }

/* ===== 标题 ===== */
.main-title{
  font-family: 'Orbitron','Noto Sans SC',sans-serif;
  font-size: 2.4rem;
  font-weight: 900;
  background: linear-gradient(90deg, #a5b4fc, #c4b5fd, #f0abfc);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  text-align:center;
  margin-bottom: .35rem;
  text-shadow: 0 0 26px rgba(129, 140, 248, 0.28);
}
.sub-title{
  font-family: 'Noto Sans SC',sans-serif;
  font-size: 1.02rem;
  color: var(--muted);
  text-align:center;
  margin-bottom: 1.35rem;
}

/* ===== 侧边栏：稳定选择器 ===== */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #10182f, #0b1020) !important;
  border-right: 1px solid rgba(148,163,184,.14);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{ color: #c7d2fe !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] span{ color: var(--text); }
section[data-testid="stSidebar"] .stCaption{ color: var(--muted) !important; }

/* sidebar 输入框/下拉框 */
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
div[data-baseweb="option"]{ color: var(--text) !important; }
div[data-baseweb="option"]:hover{ background: rgba(99,102,241,.18) !important; }

/* 日期 popover */
div[data-baseweb="popover"]{
  background: rgba(15,23,42,.98) !important;
  border: 1px solid rgba(148,163,184,.20) !important;
  border-radius: 12px !important;
  z-index: 9999 !important;
}
div[data-baseweb="popover"] div[role="option"]:hover{
  background: rgba(99,102,241,.18) !important;
}

/* 禁用日期 */
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
div[data-baseweb="popover"] button.date-disabled .date-disabled-icon {
  display: inline-block !important;
  font-size: 10px !important;
  margin-left: 2px !important;
  vertical-align: middle !important;
  opacity: 0.8 !important;
}

/* ===== 按钮 ===== */
.stButton > button{
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  color: #fff !important;
  border: none;
  border-radius: 12px;
  padding: 0.72rem 1.2rem;
  font-weight: 800;
  transition: all .22s ease;
  box-shadow: 0 8px 22px rgba(99,102,241,.30);
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(99,102,241,.38);
}

/* ===== 统计概览卡 ===== */
.stats-overview{
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border-radius: 18px;
  padding: 0.8rem 1rem 0.8rem 1rem;
  margin: 1.1rem 0 1.1rem 0;
  border: 1px solid rgba(148,163,184,.16);
  box-shadow: 0 12px 30px rgba(0,0,0,.30);
}
.stats-overview h2{
  color: #e9d5ff;
  margin: 0 0 .6rem 0;
  padding-bottom: .5rem;
  border-bottom: 1px solid rgba(148,163,184,.18);
  font-size: 1.5rem;
  font-weight: 600;
}
.stat-grid{
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap: .9rem;
}
.stat-item{
  background: rgba(99,102,241,.09);
  border: 1px solid rgba(148,163,184,.12);
  border-radius: 14px;
  padding: .95rem .9rem;
  text-align:center;
}
.stat-value{
  font-size: 1.85rem;
  font-weight: 900;
  color: #c7d2fe;
  letter-spacing: .5px;
}
.stat-label{
  font-size: .88rem;
  color: var(--muted);
}

/* ===== 摘要卡 ===== */
.cluster-wrapper{
  margin: 14px 0 10px 0;
  position: relative;
}
.cluster-card{
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 18px;
  padding: 14px 16px 12px 16px;
  box-shadow: 0 12px 28px rgba(0,0,0,.28);
  margin-bottom: 8px;
}
.cluster-header{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 10px;
  margin-bottom: 8px;
}

/* Expander内部的sticky header（冻结首行） */
.cluster-header-sticky{
  position: sticky;
  top: 0;
  z-index: 100;
  margin: -12px -14px 12px -14px;
  padding: 0;
}
.cluster-header-inner{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 10px;
  padding: 12px 14px;
  background: linear-gradient(145deg, rgba(18,26,49,.98), rgba(15,23,42,.98));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(148,163,184,.2);
  box-shadow: 0 4px 12px rgba(0,0,0,.2);
}
.cluster-header-inner .cluster-title{
  font-weight: 950;
  font-size: 1.15rem;
  color: #f1f5f9;
  line-height: 1.25;
}
.cluster-header-inner .cluster-meta{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.cluster-title{
  font-weight: 950;
  font-size: 1.15rem;
  color: #f1f5f9;
  line-height: 1.25;
}
.cluster-meta{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.meta-chip{
  background: rgba(99,102,241,.10);
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 999px;
  padding: 6px 10px;
  font-size: .86rem;
  color: var(--text);
}
.meta-chip span{
  color: var(--muted);
  font-weight: 700;
  margin-right: 6px;
}
.badge-heat{
  flex: 0 0 auto;
  padding: 7px 10px;
  border-radius: 999px;
  font-weight: 950;
  color:#fff;
  background: linear-gradient(90deg, rgba(236,72,153,.95), rgba(139,92,246,.95));
  box-shadow: 0 8px 20px rgba(236,72,153,.22);
  white-space: nowrap;
}
.badge-heat small{
  opacity:.88;
  font-weight: 800;
  margin-right: 4px;
}

.heatbar-wrap{
  margin-top: 10px;
  background: rgba(148,163,184,.10);
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
  border: 1px solid rgba(148,163,184,.10);
}
.heatbar{
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(99,102,241,.95), rgba(236,72,153,.92));
}

/* ===== Expander（展开详情条更贴近你截图）===== */
section[data-testid="stMain"] div[data-testid="stExpander"] details > summary{
  background: rgba(15,23,42,.75) !important;
  border: 1px solid rgba(148,163,184,.16) !important;
  border-radius: 14px !important;
  padding: 10px 14px !important;
}
section[data-testid="stMain"] div[data-testid="stExpander"] details > summary *{
  color: var(--text) !important;
  font-weight: 900 !important;
}
section[data-testid="stMain"] div[data-testid="stExpander"] div[role="region"]{
  background: rgba(15,23,42,.30) !important;
  border: 1px solid rgba(148,163,184,.10) !important;
  border-radius: 14px !important;
  padding: 12px 14px !important;
  position: relative;
}

/* ===== 讨论点 / 观点 / 引用 ===== */
.discussion-point{
  background: rgba(236,72,153,.12);
  border: 1px solid rgba(236,72,153,.18);
  padding: .78rem .95rem;
  margin: .7rem 0 .55rem 0;
  border-radius: 12px;
}
.discussion-point strong{ color:#fff; font-size: 1.02rem; }

.opinion-item{
  background: rgba(34,211,238,.10);
  border: 1px solid rgba(34,211,238,.16);
  padding: .72rem .92rem;
  margin: .45rem 0;
  border-radius: 12px;
  color: var(--text);
}
.example-quote{
  background: rgba(99,102,241,.10);
  border: 1px solid rgba(99,102,241,.16);
  padding: .68rem .9rem;
  margin: .42rem 0;
  border-radius: 12px;
  color: #dbeafe;
  font-style: italic;
}

/* Metric */
[data-testid="stMetricValue"]{ color: #c7d2fe !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"]{ color: var(--muted) !important; }

a{ color:#a5b4fc !important; text-decoration: none !important; }
a:hover{ text-decoration: underline !important; }
</style>
"""

# ==================== 网络读取（带刷新 nonce 防缓存）===================

def _get_nonce() -> str:
    return st.session_state.get("_nonce", "")

def _set_nonce():
    st.session_state["_nonce"] = str(int(time.time()))

def fetch_json(url: str) -> dict | None:
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

    local_path = LOCAL_RESULTS_DIR / group["dir"] / "index.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

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

    local_path = LOCAL_RESULTS_DIR / group["dir"] / f"{date}.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/{date}.json"
        data = fetch_json(url)
        return data or {}
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return {}

# ==================== 渲染 ====================

def render_result(result: dict, group_key: str | None = None):
    if not result:
        st.warning("⚠️ 暂无数据")
        return

    date = result.get("date", "")
    clusters = result.get("clusters", [])
    summary = result.get("summary", {})

    total_clusters = summary.get("total_clusters", len(clusters))
    total_players = summary.get("total_players", 0)
    total_messages = summary.get("total_messages", 0)

    # 群名称格式化：🌍 地球群1 -> 《地球》1群
    group_display = ""
    if group_key and group_key in GROUPS:
        group_name = GROUPS[group_key]["name"]
        import re
        cleaned_name = re.sub(r'[^\w\s\u4e00-\u9fff]', '', group_name).strip()
        match = re.search(r'([\u4e00-\u9fff]+)群(\d+)', cleaned_name)
        if match:
            group_type = match.group(1)
            group_num = match.group(2)
            group_display = f"《{group_type}》{group_num}群 "
        else:
            match2 = re.search(r'([\u4e00-\u9fff]+)(\d+)', cleaned_name)
            if match2:
                group_type = match2.group(1)
                group_num = match2.group(2)
                group_display = f"《{group_type}》{group_num}群 "
            else:
                group_display = cleaned_name + " "

    # 获取平台信息
    platform = result.get("source", "QQ")  # 默认为QQ
    platform_display = {
        "QQ": "QQ",
        "微信": "微信",
        "WeChat": "微信",
        "Discord": "Discord",
        "discord": "Discord"
    }.get(platform, platform)
    
    # 格式化日期显示（YYYY年MM月DD日）
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y年%m月%d日")
    except:
        formatted_date = date
    
    # 获取热度公式（如果有）
    heat_formula = result.get("heat_formula", "热度值 = 发言玩家数 × sqrt(发言总数)")
    
    # 报告说明
    st.markdown(
        f"""<div class="stats-overview">
<h2>📊 {group_display}{date} 分析报告</h2>
<div style="padding: 0.3rem 0; line-height: 1.6; color: var(--text);">
  <p style="margin: 0.3rem 0; font-size: 1.05rem;">
    <strong>{formatted_date}</strong> <strong>{platform_display}</strong> <strong>{group_display.strip()}</strong> 每日输出结果
  </p>
  <p style="margin: 0.3rem 0; font-size: 1.05rem; color: var(--muted);">
    默认展示当日热度最高的Top5话题（可展开查看讨论点/玩家观点/代表性发言）
  </p>
  <p style="margin: 0.3rem 0; font-size: 0.95rem; color: var(--muted2); font-style: italic;">
    {heat_formula}
  </p>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # ========= 热门话题列表（摘要卡 + 展开详情）=========
    sorted_clusters = sorted(clusters, key=lambda x: float(x.get("热度评分", 0) or 0), reverse=True)

    # 如果你只想显示 Top5，把这行打开即可：
    # sorted_clusters = sorted_clusters[:5]

    st.markdown(f"#### 🔥 热门话题Top5")

    top1_heat = float(sorted_clusters[0].get("热度评分", 0) or 0) if sorted_clusters else 1.0
    if top1_heat <= 0:
        top1_heat = 1.0

    for idx, cluster in enumerate(sorted_clusters, 1):
        title = cluster.get("聚合话题簇", "(未命名话题)")
        heat = float(cluster.get("热度评分", 0) or 0)
        players = cluster.get("发言玩家总数", 0)
        msgs = cluster.get("发言总数", 0)
        time_axis = cluster.get("时间轴", "")

        pct = max(0.0, min(100.0, (heat / top1_heat) * 100.0))

        meta_chips = []
        meta_chips.append(f'<div class="meta-chip"><span>👥 玩家</span>{players}</div>')
        meta_chips.append(f'<div class="meta-chip"><span>💬 发言</span>{msgs}</div>')
        if time_axis:
            short_time = time_axis if len(time_axis) <= 70 else (time_axis[:70] + "…")
            meta_chips.append(f'<div class="meta-chip"><span>⏰ 时间</span>{short_time}</div>')

        # 包装容器，用于实现sticky效果
        st.markdown(
            f"""<div class="cluster-wrapper">
<div class="cluster-card">
<div class="cluster-header">
  <div>
    <div class="cluster-title">{idx}. {title}</div>
    <div class="cluster-meta">{''.join(meta_chips)}</div>
  </div>
  <div class="badge-heat"><small>热度</small>{heat:.1f} 🔥</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )

        # 展开详情（全量展示）
        with st.expander("展开详情（讨论点/观点/代表发言）", expanded=(idx <= 2)):
            # 在expander内部添加sticky header（冻结首行）
            st.markdown(
                f"""<div class="cluster-header-sticky">
<div class="cluster-header-inner">
  <div>
    <div class="cluster-title">{idx}. {title}</div>
    <div class="cluster-meta">{''.join(meta_chips)}</div>
  </div>
  <div class="badge-heat"><small>热度</small>{heat:.1f} 🔥</div>
</div>
</div>""",
                unsafe_allow_html=True,
            )
            if time_axis:
                st.markdown(f"**⏰ 完整时间轴：** {time_axis}")
            else:
                st.markdown("**⏰ 完整时间轴：**（无）")

            discussion_list = cluster.get("讨论点列表", []) or []
            if not discussion_list:
                st.info("暂无讨论点列表")
                continue

            st.markdown(f"#### 💬 讨论点与玩家观点（共 {len(discussion_list)} 条）")

            for dp_i, dp in enumerate(discussion_list, 1):
                # 找到 “讨论点X”
                dp_title = ""
                for k in dp.keys():
                    if str(k).startswith("讨论点"):
                        dp_title = (dp.get(k) or "").strip()
                        break

                if dp_title:
                    st.markdown(
                        f"""<div class="discussion-point"><strong>📌 {dp_i}. {dp_title}</strong></div>""",
                        unsafe_allow_html=True,
                    )

                opinions = dp.get("玩家观点", []) or []
                if opinions:
                    st.markdown("**玩家观点：**")
                    for opinion in opinions:
                        st.markdown(
                            f"""<div class="opinion-item">{opinion}</div>""",
                            unsafe_allow_html=True,
                        )

                examples = dp.get("代表性玩家发言示例", []) or []
                if examples:
                    st.markdown(f"**代表性发言（{len(examples)}）：**")
                    for example in examples:
                        st.markdown(
                            f"""<div class="example-quote">"{example}"</div>""",
                            unsafe_allow_html=True,
                        )

                st.markdown("---")

    # ========= 导出 =========
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

        for idx, cluster in enumerate(sorted_clusters, 1):
            report_lines.append(f"## {idx}. {cluster.get('聚合话题簇','(未命名话题)')}\n\n")
            report_lines.append(f"- **热度评分**: {cluster.get('热度评分', 0)}\n")
            report_lines.append(f"- **发言玩家数**: {cluster.get('发言玩家总数', 0)}\n")
            report_lines.append(f"- **发言总数**: {cluster.get('发言总数', 0)}\n")
            report_lines.append(f"- **时间轴**: {cluster.get('时间轴','')}\n\n")

            discussion_list = cluster.get("讨论点列表", []) or []
            if discussion_list:
                report_lines.append(f"### 讨论点与玩家观点（共 {len(discussion_list)} 条）\n\n")
                for dp in discussion_list:
                    dp_title = ""
                    for k in dp.keys():
                        if str(k).startswith("讨论点"):
                            dp_title = dp.get(k, "")
                            break
                    if dp_title:
                        report_lines.append(f"#### 📌 {dp_title}\n\n")

                    opinions = dp.get("玩家观点", []) or []
                    if opinions:
                        report_lines.append("**玩家观点:**\n")
                        for opinion in opinions:
                            report_lines.append(f"- {opinion}\n")
                        report_lines.append("\n")

                    examples = dp.get("代表性玩家发言示例", []) or []
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
        initial_sidebar_state="collapsed",
    )

    st.markdown(STYLE_CSS, unsafe_allow_html=True)

    st.markdown(
        """<div class="main-title">🎮 玩家社群分析系统</div>
<div class="sub-title">查看每日群聊话题分析结果（从 GitHub 自动同步）</div>""",
        unsafe_allow_html=True,
    )

    # 侧边栏
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

            # 转 date 对象
            date_objects = []
            for date_str in available_dates:
                try:
                    date_objects.append(datetime.strptime(date_str, "%Y-%m-%d").date())
                except:
                    pass

            if date_objects:
                from datetime import date as date_type

                sorted_date_objects = sorted(date_objects, reverse=True)
                default_date = sorted_date_objects[0]

                min_date = min(date_objects)
                max_date = max(date_objects)

                min_year = min_date.year
                max_year = max_date.year
                extended_min_date = date_type(min_year, 1, 1)
                extended_max_date = date_type(max_year, 12, 31)

                if "selected_date_cache" not in st.session_state:
                    st.session_state.selected_date_cache = default_date.strftime("%Y-%m-%d")

                try:
                    cached_date_obj = datetime.strptime(st.session_state.selected_date_cache, "%Y-%m-%d").date()
                    initial_date = cached_date_obj if cached_date_obj in date_objects else default_date
                except:
                    initial_date = default_date

                def on_date_change():
                    selected_date_obj_check = st.session_state.get("selected_date_input", initial_date)
                    if isinstance(selected_date_obj_check, str):
                        try:
                            selected_date_obj_check = datetime.strptime(selected_date_obj_check, "%Y-%m-%d").date()
                        except:
                            selected_date_obj_check = initial_date

                    selected_date_str_check = selected_date_obj_check.strftime("%Y-%m-%d")

                    if selected_date_str_check not in available_dates:
                        selected_date_obj_dt = datetime.combine(selected_date_obj_check, datetime.min.time())
                        closest_date = min(
                            date_objects,
                            key=lambda x: abs((datetime.combine(x, datetime.min.time()) - selected_date_obj_dt).days)
                        )
                        closest_date_str = closest_date.strftime("%Y-%m-%d")
                        st.session_state.selected_date_cache = closest_date_str
                        st.session_state.need_date_correction = True
                        st.session_state.invalid_date_selected = selected_date_str_check
                        st.session_state.valid_date_selected = closest_date_str
                        st.rerun()
                    else:
                        st.session_state.selected_date_cache = selected_date_str_check
                        st.session_state.need_date_correction = False

                if st.session_state.get("need_date_correction", False):
                    corrected_date = datetime.strptime(st.session_state.valid_date_selected, "%Y-%m-%d").date()
                    selected_date_obj = st.date_input(
                        "选择日期",
                        value=corrected_date,
                        min_value=extended_min_date,
                        max_value=extended_max_date,
                        help="只能选择已上传到数据库的日期（带禁止符号的日期不可选）",
                        key="selected_date_input",
                        on_change=on_date_change
                    )

                    invalid_date = st.session_state.get("invalid_date_selected", "")
                    valid_date = st.session_state.get("valid_date_selected", "")
                    if invalid_date:
                        formatted_invalid_date = datetime.strptime(invalid_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
                        formatted_valid_date = datetime.strptime(valid_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
                        st.markdown(
                            f'<div style="padding: 1rem; background-color: rgba(255, 193, 7, 0.10); '
                            f'border-left: 4px solid #ffc107; border-radius: 10px; margin: 1rem 0;">'
                            f'<p style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #ffd166;">'
                            f'⚠️ {formatted_invalid_date}暂无数据，推荐选择最近的可用日期：{formatted_valid_date}</p></div>',
                            unsafe_allow_html=True
                        )
                    st.session_state.need_date_correction = False
                else:
                    selected_date_obj = st.date_input(
                        "选择日期",
                        value=initial_date,
                        min_value=extended_min_date,
                        max_value=extended_max_date,
                        help="只能选择已上传到数据库的日期（带禁止符号的日期不可选）",
                        key="selected_date_input",
                        on_change=on_date_change
                    )

                # JS 禁用不可用日期
                available_dates_js = json.dumps(available_dates)
                disable_dates_js = f"""
<script>
(function(){{
  const availableDates = {available_dates_js};

  function disableUnavailableDates(){{
    const popover = document.querySelector('div[data-baseweb="popover"]');
    if(!popover) return;
    const table = popover.querySelector('table');
    if(!table) return;

    let currentYear = null;
    let currentMonth = null;

    const headerButtons = popover.querySelectorAll('button[role="combobox"]');
    headerButtons.forEach(btn => {{
      const text = (btn.textContent || btn.getAttribute('aria-label') || '').trim();
      const yearMatch = text.match(/(\\d{{4}})/);
      if(yearMatch) currentYear = parseInt(yearMatch[1]);
      const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
      const monthNamesCN = ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'];
      for(let i=0;i<monthNames.length;i++) {{
        if(text.toLowerCase().includes(monthNames[i].toLowerCase()) || text.includes(monthNamesCN[i])) {{
          currentMonth = i; break;
        }}
      }}
    }});

    if(currentYear === null || currentMonth === null) {{
      const dateInput = document.querySelector('input[type="date"]');
      if(dateInput && dateInput.value) {{
        const inputDate = new Date(dateInput.value);
        if(currentYear === null) currentYear = inputDate.getFullYear();
        if(currentMonth === null) currentMonth = inputDate.getMonth();
      }}
    }}
    if(currentYear === null || currentMonth === null) {{
      const now = new Date();
      if(currentYear === null) currentYear = now.getFullYear();
      if(currentMonth === null) currentMonth = now.getMonth();
    }}

    const tbody = table.querySelector('tbody');
    if(!tbody) return;

    const dateButtons = tbody.querySelectorAll('button');
    dateButtons.forEach(button => {{
      let dayText = button.textContent.trim();
      dayText = dayText.replace(/🚫/g,'').replace(/\\s+/g,'').trim();
      if(button.dataset.originalText) dayText = button.dataset.originalText;
      const day = parseInt(dayText);
      if(isNaN(day) || day<1 || day>31) return;

      const dateStr = `${{currentYear}}-${{String(currentMonth+1).padStart(2,'0')}}-${{String(day).padStart(2,'0')}}`;

      if(!availableDates.includes(dateStr)) {{
        if(!button.dataset.originalText) button.dataset.originalText = dayText;
        button.disabled = true;
        button.setAttribute('aria-disabled','true');
        button.style.opacity = '0.4';
        button.style.pointerEvents = 'none';
        button.classList.add('date-disabled');

        const existingIcon = button.querySelector('.date-disabled-icon');
        if(existingIcon) existingIcon.remove();
        const icon = document.createElement('span');
        icon.className = 'date-disabled-icon';
        icon.textContent = '🚫';
        icon.style.cssText = 'font-size:12px;margin-left:3px;vertical-align:middle;display:inline-block;';
        button.innerHTML = button.dataset.originalText + ' ' + icon.outerHTML;
      }} else {{
        button.disabled = false;
        button.removeAttribute('aria-disabled');
        button.style.opacity = '1';
        button.style.pointerEvents = 'auto';
        button.classList.remove('date-disabled');

        const icon = button.querySelector('.date-disabled-icon');
        if(icon) icon.remove();
        if(button.dataset.originalText) {{
          button.textContent = button.dataset.originalText;
          delete button.dataset.originalText;
        }}
      }}
    }});
  }}

  const observer = new MutationObserver(function(){{
    const hasPopover = document.querySelector('div[data-baseweb="popover"]');
    if(hasPopover) disableUnavailableDates();
  }});
  observer.observe(document.body, {{ childList:true, subtree:true }});

  document.addEventListener('click', function(e){{
    const t = e.target;
    if(t.closest('[data-baseweb="popover"]') ||
       t.closest('input[type="date"]') ||
       t.closest('button[aria-label*="date"]') ||
       t.closest('button[role="combobox"]')) {{
      setTimeout(disableUnavailableDates, 60);
      setTimeout(disableUnavailableDates, 250);
    }}
  }}, true);

  setTimeout(disableUnavailableDates, 80);
  setTimeout(disableUnavailableDates, 300);
  setInterval(function(){{
    const popover = document.querySelector('div[data-baseweb="popover"]');
    if(popover && popover.style.display !== 'none') disableUnavailableDates();
  }}, 500);
}})();
</script>
"""
                st.markdown(disable_dates_js, unsafe_allow_html=True)

                selected_date = selected_date_obj.strftime("%Y-%m-%d")
                if selected_date in available_dates:
                    st.session_state.selected_date_cache = selected_date
            else:
                selected_date = None
        else:
            st.warning("⚠️ 暂无数据")
            selected_date = None

        st.markdown("---")
        st.caption("💡 数据每日自动更新到 GitHub")

        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            _set_nonce()
            st.rerun()

    # 主内容区
    if selected_date:
        with st.spinner(f"正在加载 {selected_date} 的数据..."):
            result = load_result(selected_group_key, selected_date)

        if result:
            render_result(result, selected_group_key)
        else:
            st.error(f"❌  {selected_date} 的数据待上传")
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