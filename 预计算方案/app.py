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
import html

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
  --primary:#6366f1;
  --secondary:#8b5cf6;
  --accent:#ec4899;
  --accent-primary:#a855f7;
  --accent-secondary:#3b82f6;

  --bg-dark:#020617;
  --bg0:#0b1020;
  --bg1:#111b34;
  --bg2:#1e1b4b;

  --card:#121a31;
  --card2:#0f172a;
  --card-bg:rgba(15, 23, 42, 0.7);
  --line:rgba(148,163,184,.18);
  --glass-border:rgba(255, 255, 255, 0.08);

  --text:#e5e7eb;
  --muted:#94a3b8;
  --muted2:#64748b;
  --text-dim:#94a3b8;
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
  position: sticky !important;
  top: 0 !important;
  z-index: 100 !important;
  margin: 0 !important;
  padding: 0 !important;
  margin-bottom: 12px !important;
  background: transparent !important;
}
.cluster-header-inner{
  display:flex !important;
  align-items:flex-start !important;
  justify-content:space-between !important;
  gap: 10px !important;
  padding: 12px 14px !important;
  background: linear-gradient(145deg, rgba(18,26,49,.98), rgba(15,23,42,.98)) !important;
  backdrop-filter: blur(10px) !important;
  border-bottom: 1px solid rgba(148,163,184,.2) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,.2) !important;
}
.cluster-header-inner .cluster-title{
  font-weight: 950 !important;
  font-size: 1.15rem !important;
  color: #f1f5f9 !important;
  line-height: 1.25 !important;
}
.cluster-header-inner .cluster-meta{
  display:flex !important;
  gap: 8px !important;
  flex-wrap: wrap !important;
  margin-top: 8px !important;
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

/* ===== 自定义 Expander（完全控制，支持 sticky）===== */
.cluster-custom-wrapper{
  margin: 14px 0;
  position: relative;
}
.custom-expander{
  border-radius: 18px;
}
/* Summary中的卡片：未展开时显示，展开后隐藏 */
.custom-expander:not([open]) .custom-expander-summary .cluster-card{
  display: block;
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 18px;
  padding: 14px 16px 12px 16px;
  box-shadow: 0 12px 28px rgba(0,0,0,.28);
  margin-bottom: 8px;
}
.custom-expander[open] .custom-expander-summary .cluster-card{
  display: none;
}
/* Details包装器：展开后显示 */
.details-wrapper{
  position: relative;
  margin-top: 8px;
}
/* Sticky卡片：固定在最顶部 */
.cluster-card-sticky{
  position: sticky !important;
  top: 0 !important;
  z-index: 100 !important;
  background: linear-gradient(180deg, rgba(15,23,42,1) 0%, rgba(15,23,42,0.98) 85%, rgba(15,23,42,0.7) 100%) !important;
  padding-bottom: 10px;
  margin-bottom: 0;
}
.cluster-card-sticky .cluster-card{
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 18px;
  padding: 14px 16px 12px 16px;
  box-shadow: 0 12px 28px rgba(0,0,0,.28);
}
/* 可滚动内容区域 */
.scrollable-content{
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(15,23,42,.30);
  border: 1px solid rgba(148,163,184,.10);
  border-radius: 14px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148,163,184,.3) transparent;
}
.scrollable-content::-webkit-scrollbar{
  width: 8px;
}
.scrollable-content::-webkit-scrollbar-track{
  background: transparent;
}
.scrollable-content::-webkit-scrollbar-thumb{
  background: rgba(148,163,184,.3);
  border-radius: 4px;
}
/* 内部收起按钮 */
.expander-toggle-inside{
  background: rgba(15,23,42,.75);
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 18px;
  padding: 10px 16px;
  margin: 12px 14px;
  text-align: left;
  color: var(--text);
  font-weight: 900;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.expander-toggle-inside:hover{
  background: rgba(15,23,42,.9);
}
.expander-toggle-inside .toggle-icon{
  display: inline-block;
  margin-right: 8px;
  font-size: 0.8rem;
}
.expander-toggle-inside .toggle-text{
  font-size: 0.95rem;
}
.custom-expander{
  border-radius: 18px;
}
.custom-expander-summary{
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  color: var(--text) !important;
  cursor: pointer !important;
  list-style: none !important;
  user-select: none !important;
  display: block !important;
}
.custom-expander-summary::-webkit-details-marker{
  display: none;
}
.expander-toggle{
  background: rgba(15,23,42,.75);
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 18px;
  padding: 10px 16px;
  text-align: left;
  color: var(--text);
  font-weight: 900;
  transition: all 0.2s ease;
}
.expander-toggle:hover{
  background: rgba(15,23,42,.9);
}
.toggle-icon{
  display: inline-block;
  margin-right: 8px;
  font-size: 0.8rem;
}
.toggle-text{
  font-size: 0.95rem;
}
/* 展开后隐藏summary中的展开按钮 */
.custom-expander[open] .custom-expander-summary .expander-toggle{
  display: none;
}
.custom-expander-inner{
  padding: 12px 14px;
}
.custom-expander-inner p,
.custom-expander-inner h4{
  color: var(--text);
}

/* ===== Expander（原生 Streamlit，保留兼容）===== */
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

/* 脉动动画 */
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

/* ===== 主页样式（新版） ===== */
.system-container{
  min-height: 100vh;
  position: relative;
  z-index: 1;
  font-family: 'Inter', system-ui, sans-serif;
}

/* Header */
.system-header{
  padding: 32px 5% 16px;
  background: linear-gradient(to bottom, rgba(168, 85, 247, 0.1), transparent);
  text-align: center;
}
.logo-group{
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.pulse-icon{
  font-size: 2.2rem;
  background: rgba(168, 85, 247, 0.2);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  border: 1px solid var(--accent-primary);
  box-shadow: 0 0 30px rgba(168, 85, 247, 0.3);
}
.title-stack{
  text-align: center;
}
.title-stack h1{
  margin: 0;
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: white;
}
.title-stack h1 span{
  background: linear-gradient(to right, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.status-badges{
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}
.badge{
  font-size: 0.7rem;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 99px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid var(--glass-border);
}
.badge.live{
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}

/* Control Center */
.control-center{
  width: 90%;
  max-width: 1200px;
  margin: 24px auto;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}
.query-modes{
  display: flex;
  gap: 4px;
  background: rgba(0,0,0,0.3);
  padding: 4px;
  border-radius: 12px;
  width: fit-content;
  margin-bottom: 20px;
}
.query-modes button{
  background: transparent;
  border: none;
  color: var(--text-dim);
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}
.query-modes button.active{
  background: rgba(255,255,255,0.1);
  color: white;
}
.filter-shelf{
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 20px;
  align-items: flex-end;
}
.input-group label{
  display: block;
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-bottom: 8px;
  padding-left: 4px;
}
.input-group select, .input-group input{
  width: 100%;
  background: rgba(0,0,0,0.4);
  border: 1px solid var(--glass-border);
  color: white;
  padding: 14px 16px;
  border-radius: 12px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.3s;
}
.input-group select:focus, .input-group input:focus{
  border-color: var(--accent-primary);
}
.primary-run{
  background: linear-gradient(to right, var(--accent-primary), #7c3aed);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 10px 20px rgba(168, 85, 247, 0.3);
  transition: transform 0.2s, opacity 0.3s;
}
.primary-run:hover{ transform: translateY(-2px); }
.primary-run:disabled{ opacity: 0.5; cursor: not-allowed; }

/* Intro Cards */
.intro-grid{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  width: 90%;
  max-width: 1200px;
  margin: 32px auto;
}
@media (max-width: 1024px){
  .intro-grid{ grid-template-columns: repeat(2, 1fr); }
  .filter-shelf{ grid-template-columns: 1fr; }
}
@media (max-width: 640px){
  .intro-grid{ grid-template-columns: 1fr; }
}
.intro-card{
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--glass-border);
  padding: 24px;
  border-radius: 20px;
  transition: all 0.3s;
}
.intro-card .icon{
  font-size: 1.8rem;
  margin-bottom: 16px;
  display: block;
}
.intro-card h3{ margin: 0 0 8px; font-size: 1rem; font-weight: 700; color: white; }
.intro-card p{ color: var(--text-dim); font-size: 0.85rem; line-height: 1.5; margin: 0; }
.intro-card:hover{
  background: rgba(255,255,255,0.05);
  transform: translateY(-5px);
  border-color: var(--accent-primary);
}

/* Homepage Tabs Styling */
.control-center .stTabs [data-baseweb="tab-list"]{
  display: flex !important;
  gap: 4px;
  background: transparent !important;
  padding: 4px;
  border-radius: 12px;
  width: fit-content;
  margin-bottom: 20px;
  border: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
}
.control-center .stTabs [data-baseweb="tab-border"],
.control-center .stTabs [data-baseweb="tab-highlight"]{
  display: none !important;
}
.control-center .stTabs [data-baseweb="tab"]{
  flex: none !important;
  height: auto;
  padding: 10px 20px;
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  color: var(--text-dim);
  font-weight: 600;
  font-size: 0.9rem;
  justify-content: center;
  border: 1px solid var(--glass-border);
}
.control-center .stTabs [aria-selected="true"]{
  background: rgba(168,85,247,0.2) !important;
  color: white !important;
  border-color: var(--accent-primary) !important;
}
.control-center .stTabs [aria-selected="true"]::after{
  display: none !important;
}
.control-center .stTabs [data-baseweb="tab-panel"]{
  padding: 16px 0 !important;
}
/* 隐藏 tabs 底部横线 */
.control-center .stTabs > div:first-child{
  background: transparent !important;
}
.control-center .stTabs > div > div:first-child{
  background: transparent !important;
  border: none !important;
}
.control-center .stTabs [role="tablist"]{
  background: transparent !important;
  gap: 8px !important;
}
.control-center .stTabs [role="tablist"]::before,
.control-center .stTabs [role="tablist"]::after{
  display: none !important;
}
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
    
    # 报告说明（紧凑版）
    st.markdown(
        f"""<div class="stats-overview">
<h2>📊 {platform_display} {group_display} {formatted_date} 分析报告</h2>
<div style="padding: 0.3rem 0; line-height: 1.8; color: var(--text);">
  <p style="margin: 0.2rem 0; font-size: 1.0rem;">
    默认展示当日热度最高的Top5话题（可展开查看讨论点/玩家观点/代表性发言） • <span style="color: var(--muted2); font-style: italic;">{heat_formula}</span>
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

        # 使用纯HTML创建可展开的自定义容器（绕过st.expander限制）
        expanded_str = "open" if idx <= 2 else ""
        
        # 构建讨论点内容HTML
        discussion_content_html = ""
        
        discussion_list = cluster.get("讨论点列表", []) or []
        
        if discussion_list:
            discussion_content_html += f'<h4 style="color: var(--text); margin: 1rem 0;">💬 讨论点与玩家观点（共 {len(discussion_list)} 条）</h4>'
            
            for dp_i, dp in enumerate(discussion_list, 1):
                # 找到 "讨论点X"
                dp_title = ""
                for k in dp.keys():
                    if str(k).startswith("讨论点"):
                        dp_title = (dp.get(k) or "").strip()
                        break
                
                if dp_title:
                    discussion_content_html += f'<div class="discussion-point"><strong>📌 {dp_i}. {html.escape(dp_title)}</strong></div>'
                
                opinions = dp.get("玩家观点", []) or []
                if opinions:
                    discussion_content_html += '<p style="color: var(--text); font-weight: 600; margin: 0.5rem 0;">玩家观点：</p>'
                    for opinion in opinions:
                        discussion_content_html += f'<div class="opinion-item">{html.escape(opinion)}</div>'
                
                examples = dp.get("代表性玩家发言示例", []) or []
                if examples:
                    discussion_content_html += f'<p style="color: var(--text); font-weight: 600; margin: 0.5rem 0;">代表性发言（{len(examples)}）：</p>'
                    for example in examples:
                        discussion_content_html += f'<div class="example-quote">"{html.escape(example)}"</div>'
                
                discussion_content_html += '<hr style="border: none; border-top: 1px solid rgba(148,163,184,.1); margin: 1rem 0;">'
        else:
            discussion_content_html = '<p style="color: var(--muted);">暂无讨论点列表</p>'
        
        # 完整时间轴（转义特殊字符）
        time_axis_html = f'<p style="color: var(--text);"><strong>⏰ 完整时间轴：</strong> {html.escape(time_axis)}</p>' if time_axis else '<p style="color: var(--text);"><strong>⏰ 完整时间轴：</strong>（无）</p>'
        
        # 渲染完整的自定义HTML（包含可滚动容器和sticky header）
        # 转义标题中的特殊字符
        title_escaped = html.escape(title)
        
        st.markdown(
            f"""<div class="cluster-custom-wrapper">
<details class="custom-expander" {expanded_str} id="cluster-{idx}">
<summary class="custom-expander-summary">
<div class="cluster-card">
<div class="cluster-header">
<div>
<div class="cluster-title">{idx}. {title_escaped}</div>
<div class="cluster-meta">{''.join(meta_chips)}</div>
</div>
<div class="badge-heat"><small>热度</small>{heat:.1f} 🔥</div>
</div>
</div>
<div class="expander-toggle">
<span class="toggle-icon">▼</span>
<span class="toggle-text">详情（讨论点/观点/代表发言）</span>
</div>
</summary>
<div class="details-wrapper">
<!-- Sticky卡片：固定在最顶部 -->
<div class="cluster-card-sticky">
<div class="cluster-card">
<div class="cluster-header">
<div>
<div class="cluster-title">{idx}. {title_escaped}</div>
<div class="cluster-meta">{''.join(meta_chips)}</div>
</div>
<div class="badge-heat"><small>热度</small>{heat:.1f} 🔥</div>
</div>
</div>
</div>
<!-- 可滚动内容区域（包含收起按钮 + 详细内容）-->
<div class="scrollable-content">
<div class="expander-toggle-inside">
<span class="toggle-icon">▲</span>
<span class="toggle-text">收起详情</span>
</div>
<div class="custom-expander-inner">
{time_axis_html}
{discussion_content_html}
</div>
</div>
</div>
</details>
</div>""",
            unsafe_allow_html=True,
        )
        
        # 跳过原来的 expander 逻辑
        continue_to_next = True
        if continue_to_next:
            continue
        
        # 下面的代码不会执行（保留以防需要回滚）
        with st.expander("展开详情（讨论点/观点/代表发言）", expanded=(idx <= 2)):
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

    # ========= JavaScript：处理收起详情按钮 =========
    components.html(
        """
<script>
(function() {
    // 等待父页面加载完成
    function setupCollapseButtons() {
        // 获取父页面的document
        const parentDoc = window.parent.document;
        
        // 找到所有收起按钮
        const collapseButtons = parentDoc.querySelectorAll('.expander-toggle-inside');
        
        console.log('找到收起按钮数量:', collapseButtons.length);
        
        collapseButtons.forEach((button, index) => {
            // 检查是否已经绑定过
            if (button.dataset.bound === 'true') {
                return;
            }
            button.dataset.bound = 'true';
            
            console.log('绑定第', index + 1, '个按钮');
            
            // 添加点击事件
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('收起按钮被点击');
                
                // 向上查找最近的 details 元素
                const details = this.closest('details');
                if (details) {
                    console.log('找到details元素，开始收起');
                    details.open = false;
                    details.removeAttribute('open');
                } else {
                    console.log('未找到details元素');
                }
            });
        });
    }
    
    // 多次尝试绑定，确保成功
    setTimeout(setupCollapseButtons, 100);
    setTimeout(setupCollapseButtons, 300);
    setTimeout(setupCollapseButtons, 500);
    setTimeout(setupCollapseButtons, 800);
    setTimeout(setupCollapseButtons, 1200);
    setTimeout(setupCollapseButtons, 2000);
    
    // 监听父页面DOM变化
    const parentDoc = window.parent.document;
    const observer = new MutationObserver(function() {
        setupCollapseButtons();
    });
    observer.observe(parentDoc.body, { childList: true, subtree: true });
})();
</script>
""",
        height=0,
    )
    
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

# ==================== 主页欢迎界面 ====================

def show_homepage():
    """显示欢迎主页（新版布局）——✅修正版：真正把 tabs/筛选控件包进 Control Center 卡片"""

    # ===== Header 区域 =====
    st.markdown("""
<header class="system-header">
    <div class="logo-group">
        <div class="pulse-icon">🎮</div>
        <div class="title-stack">
            <h1>玩家社群<span>分析系统</span></h1>
            <div class="status-badges">
                <span class="badge live">● AI 驱动</span>
                <span class="badge">实时同步</span>
                <span class="badge">GitHub托管</span>
            </div>
        </div>
    </div>
</header>
""", unsafe_allow_html=True)

    # ✅ Control Center（正确做法）：用 st.container() + anchor
    # 之后用 CSS :has(#cc-anchor) 把这一整块画成一个方框卡片
    with st.container():
        st.markdown('<div id="cc-anchor"></div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🗓 日常查询", "🎯 版本查询"])

        # === 日常查询标签 ===
        with tab1:
            col1, col2, col3 = st.columns([1, 1, 0.5])

            with col1:
                group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
                selected_group_daily = st.selectbox(
                    "监控社群",
                    options=list(group_options.keys()),
                    format_func=lambda x: group_options[x],
                    key="homepage_group_daily",
                )

            with col2:
                # 加载日期列表
                with st.spinner("加载可用日期..."):
                    index = load_index(selected_group_daily)
                    available_dates = index.get("available_dates", [])

                if available_dates:
                    # 转换为date对象
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

                        # 初始化session state
                        if "homepage_date_cache" not in st.session_state:
                            st.session_state.homepage_date_cache = default_date.strftime("%Y-%m-%d")

                        try:
                            cached_date_obj = datetime.strptime(
                                st.session_state.homepage_date_cache, "%Y-%m-%d"
                            ).date()
                            initial_date = cached_date_obj if cached_date_obj in date_objects else default_date
                        except:
                            initial_date = default_date

                        def on_homepage_date_change():
                            selected_date_obj_check = st.session_state.get("homepage_date_input", initial_date)
                            if isinstance(selected_date_obj_check, str):
                                try:
                                    selected_date_obj_check = datetime.strptime(
                                        selected_date_obj_check, "%Y-%m-%d"
                                    ).date()
                                except:
                                    selected_date_obj_check = initial_date

                            selected_date_str_check = selected_date_obj_check.strftime("%Y-%m-%d")

                            if selected_date_str_check not in available_dates:
                                selected_date_obj_dt = datetime.combine(
                                    selected_date_obj_check, datetime.min.time()
                                )
                                closest_date = min(
                                    date_objects,
                                    key=lambda x: abs(
                                        (datetime.combine(x, datetime.min.time()) - selected_date_obj_dt).days
                                    ),
                                )
                                closest_date_str = closest_date.strftime("%Y-%m-%d")
                                st.session_state.homepage_date_cache = closest_date_str
                                st.session_state.homepage_need_date_correction = True
                                st.session_state.homepage_invalid_date_selected = selected_date_str_check
                                st.session_state.homepage_valid_date_selected = closest_date_str
                                st.rerun()
                            else:
                                st.session_state.homepage_date_cache = selected_date_str_check
                                st.session_state.homepage_need_date_correction = False

                        if st.session_state.get("homepage_need_date_correction", False):
                            corrected_date = datetime.strptime(
                                st.session_state.homepage_valid_date_selected, "%Y-%m-%d"
                            ).date()
                            selected_date_obj = st.date_input(
                                "监测日期",
                                value=corrected_date,
                                min_value=extended_min_date,
                                max_value=extended_max_date,
                                help="选择需要查看的日期",
                                key="homepage_date_input",
                                on_change=on_homepage_date_change,
                            )

                            invalid_date = st.session_state.get("homepage_invalid_date_selected", "")
                            valid_date = st.session_state.get("homepage_valid_date_selected", "")
                            if invalid_date:
                                formatted_invalid_date = datetime.strptime(invalid_date, "%Y-%m-%d").strftime(
                                    "%Y年%m月%d日"
                                )
                                formatted_valid_date = datetime.strptime(valid_date, "%Y-%m-%d").strftime(
                                    "%Y年%m月%d日"
                                )
                                st.markdown(
                                    f'<div style="padding: 0.6rem; background-color: rgba(255, 193, 7, 0.10); '
                                    f'border-left: 3px solid #ffc107; border-radius: 8px; margin: 0.5rem 0;">'
                                    f'<p style="margin: 0; font-size: 0.85rem; font-weight: 600; color: #ffd166;">'
                                    f'⚠️ {formatted_invalid_date}暂无数据，已选择：{formatted_valid_date}</p></div>',
                                    unsafe_allow_html=True,
                                )
                            st.session_state.homepage_need_date_correction = False
                        else:
                            selected_date_obj = st.date_input(
                                "监测日期",
                                value=initial_date,
                                min_value=extended_min_date,
                                max_value=extended_max_date,
                                help="选择需要查看的日期",
                                key="homepage_date_input",
                                on_change=on_homepage_date_change,
                            )

                        # JavaScript禁用不可用日期
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
      for(let i=0;i<monthNames.length;i++){{
        if(text.toLowerCase().includes(monthNames[i].toLowerCase()) || text.includes(monthNamesCN[i])){{
          currentMonth = i; break;
        }}
      }}
    }});
    
    if(currentYear === null || currentMonth === null){{
      const dateInput = document.querySelector('input[aria-label="监测日期"]');
      if(dateInput && dateInput.value){{
        const inputDate = new Date(dateInput.value);
        if(currentYear === null) currentYear = inputDate.getFullYear();
        if(currentMonth === null) currentMonth = inputDate.getMonth();
      }}
    }}
    if(currentYear === null || currentMonth === null){{
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
      
      if(!availableDates.includes(dateStr)){{
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
      }}else{{
        button.disabled = false;
        button.removeAttribute('aria-disabled');
        button.style.opacity = '1';
        button.style.pointerEvents = 'auto';
        button.classList.remove('date-disabled');
        
        const icon = button.querySelector('.date-disabled-icon');
        if(icon) icon.remove();
        if(button.dataset.originalText){{
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
       t.closest('button[role="combobox"]')){{
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
                            st.session_state.homepage_date_cache = selected_date
                    else:
                        selected_date = None
                else:
                    st.warning("该社群暂无数据")
                    selected_date = None

            with col3:
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                if st.button(
                    "✨ 查看分析",
                    use_container_width=True,
                    type="primary",
                    disabled=not selected_date,
                    key="btn_daily",
                ):
                    st.session_state.show_results = True
                    st.session_state.query_type = "daily"
                    st.session_state.selected_group_homepage = selected_group_daily
                    st.session_state.selected_date_homepage = selected_date
                    st.rerun()

            if not selected_date and available_dates is not None and len(available_dates) == 0:
                st.info("ℹ️ 该社群暂无数据，请选择其他社群")

            # （可选）底部一句引导文案，像你截图那样
            st.markdown("<hr class='cc-divider'/>", unsafe_allow_html=True)
            st.markdown(
                "<div class='cc-hint'>或者直接向 AI 提问：<span>“分析昨晚维护后的核心负面反馈…”</span></div>",
                unsafe_allow_html=True,
            )

        # === 版本查询标签 ===
        with tab2:
            col1, col2, col3 = st.columns([1, 1, 0.5])

            with col1:
                group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
                selected_group_version = st.selectbox(
                    "监控社群",
                    options=list(group_options.keys()),
                    format_func=lambda x: group_options[x],
                    key="homepage_group_version",
                )

            with col2:
                # 版本列表（示例，可以从配置文件或数据库读取）
                version_options = [
                    "beta15_旋转木马测试（2025年12月03日~2025年12月17日）",
                    "beta17_暖冬测试（2025年12月31日~2026年1月20日）",
                ]
                selected_version = st.selectbox(
                    "版本专题总结",
                    options=version_options,
                    key="homepage_version",
                )

            with col3:
                st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
                if st.button(
                    "✨ 查看分析",
                    use_container_width=True,
                    type="primary",
                    key="btn_version",
                ):
                    st.session_state.show_results = True
                    st.session_state.query_type = "version"
                    st.session_state.selected_group_homepage = selected_group_version
                    st.session_state.selected_version_homepage = selected_version
                    st.info("版本查询功能正在开发中...")

            st.markdown("""
<div style="padding: 0.6rem 1rem; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); 
     border-radius: 10px; margin-top: 0.5rem;">
    <p style="margin: 0; font-size: 0.85rem; color: var(--text-dim);">
        💡 版本查询将展示特定版本期间的社群反馈汇总
    </p>
</div>
""", unsafe_allow_html=True)

    # ===== Intro Cards（功能介绍卡片）=====
    st.markdown("""
<div class="intro-grid">
    <div class="intro-card">
        <span class="icon">📊</span>
        <h3>话题聚类</h3>
        <p>自动识别当日讨论的主要话题，智能分组相关内容</p>
    </div>
    <div class="intro-card">
        <span class="icon">🔥</span>
        <h3>热度排名</h3>
        <p>根据参与人数和发言数计算话题热度，呈现Top5热门话题</p>
    </div>
    <div class="intro-card">
        <span class="icon">💬</span>
        <h3>观点提取</h3>
        <p>智能总结玩家的核心观点，快速了解社群态度</p>
    </div>
    <div class="intro-card">
        <span class="icon">✍️</span>
        <h3>代表发言</h3>
        <p>展示最具代表性的玩家发言，还原真实讨论场景</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== 主应用 ====================

def main():
    # 初始化session_state（需要在set_page_config之前）
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "query_type" not in st.session_state:
        st.session_state.query_type = "daily"
    
    # 根据是否显示结果决定侧边栏状态
    sidebar_state = "expanded" if st.session_state.show_results else "collapsed"
    
    st.set_page_config(
        page_title="玩家社群分析",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state=sidebar_state,
    )

    st.markdown(STYLE_CSS, unsafe_allow_html=True)
    
    # 如果未查询，显示主页
    if not st.session_state.show_results:
        show_homepage()
        return
    
    # 显示顶部标题
    st.markdown(
        """<div class="main-title">🎮 玩家社群分析系统</div>
<div class="sub-title">查看每日群聊话题分析结果（从 GitHub 自动同步）</div>""",
        unsafe_allow_html=True,
    )

    # 侧边栏
    with st.sidebar:
        st.header("🔍 查询条件")

        group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
        
        # 使用主页选择的社群作为默认值
        default_group_index = 0
        if "selected_group_homepage" in st.session_state:
            try:
                default_group_index = list(group_options.keys()).index(st.session_state.selected_group_homepage)
            except:
                pass
        
        selected_group_key = st.selectbox(
            "选择社群",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            index=default_group_index,
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
                
                # 使用主页选择的日期作为默认值
                default_date = sorted_date_objects[0]
                if "selected_date_homepage" in st.session_state:
                    try:
                        homepage_date = datetime.strptime(st.session_state.selected_date_homepage, "%Y-%m-%d").date()
                        if homepage_date in date_objects:
                            default_date = homepage_date
                    except:
                        pass

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
        
        if st.button("🏠 返回主页", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.query_type = "daily"
            st.rerun()

    # 主内容区
    # 检查查询类型
    query_type = st.session_state.get("query_type", "daily")
    
    if query_type == "version":
        # 版本查询功能（开发中）
        st.markdown("""
<div style='text-align: center; padding: 100px 20px;'>
    <div style='font-size: 4rem; margin-bottom: 24px;'>🚧</div>
    <h2 style='color: var(--text); margin-bottom: 16px;'>版本查询功能开发中</h2>
    <p style='color: var(--muted); font-size: 1.1rem; margin-bottom: 32px;'>
        该功能将汇总特定游戏版本期间的社群反馈数据，包括：
    </p>
    <div style='max-width: 600px; margin: 0 auto; text-align: left;'>
        <p style='color: var(--text); margin: 12px 0;'>📊 版本热度话题趋势</p>
        <p style='color: var(--text); margin: 12px 0;'>💬 玩家反馈汇总分析</p>
        <p style='color: var(--text); margin: 12px 0;'>📈 问题追踪与解决状态</p>
        <p style='color: var(--text); margin: 12px 0;'>🎯 版本满意度评估</p>
    </div>
</div>
""", unsafe_allow_html=True)
    elif selected_date:
        # 日常查询
        with st.spinner(f"正在加载 {selected_date} 的数据..."):
            result = load_result(selected_group_key, selected_date)

        if result:
            render_result(result, selected_group_key)
        else:
            st.error(f"❌  {selected_date} 的数据待上传")
    else:
        st.info("👈 请在侧边栏选择社群和日期")

if __name__ == "__main__":
    main()