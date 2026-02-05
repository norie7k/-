"""
玩家社群分析 - 历史结果查询 (V2)
Streamlit 应用：查看每日群聊分析结果（从 GitHub 读取）
展示：摘要卡 + 展开详情（讨论点/观点/代表发言/原文发言）
支持新版数据格式（观点列表 + 原文发言）
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

# GitHub 原始文件 URL（V2使用results2目录）
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/norie7k/-/main/预计算方案/results2"

# 本地结果目录（开发时使用，V2使用results2目录）
LOCAL_RESULTS_DIR = Path(__file__).parent / "results2"

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
section[data-testid="stMain"]{ 
  color: var(--text);
  padding-top: 0 !important;
}
section[data-testid="stMain"] p,
section[data-testid="stMain"] li{ color: var(--text); }

/* 主页专用：隐藏顶部 header（通过 class 标记控制）*/
.homepage-mode header[data-testid="stHeader"]{
  display: none !important;
}
.homepage-mode .stApp > header{
  display: none !important;
}
.homepage-mode .block-container{
  padding-top: 0 !important;
}
.homepage-mode div[data-testid="stToolbar"]{
  display: none !important;
}

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
.stButton > button span,
.stButton > button p,
.stButton button[kind="secondary"] span,
.stButton button[kind="secondary"] p,
button[data-testid="baseButton-secondary"] span,
button[data-testid="baseButton-secondary"] p{
  font-size: 1.45rem !important;
  font-weight: 700 !important;
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
  margin: 0;
  padding-bottom: 0;
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
  margin: 8px 0 6px 0;
  position: relative;
}
.cluster-card{
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 14px;
  padding: 10px 14px 8px 14px;
  box-shadow: 0 8px 20px rgba(0,0,0,.25);
  margin-bottom: 4px;
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
  font-size: 1.3rem !important;
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
  font-size: 1.3rem;
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
  margin-top: 6px;
  background: rgba(148,163,184,.08);
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  border: 1px solid rgba(148,163,184,.08);
}
.heatbar{
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #fb923c, #f97316, #dc2626);
  box-shadow: 0 2px 8px rgba(251,146,60,0.3);
}

/* ===== 自定义 Expander（完全控制，支持 sticky）===== */
.cluster-custom-wrapper{
  margin: 14px 0;
  position: relative;
}
.custom-expander{
  border-radius: 14px;
}
/* Summary中的卡片：未展开时显示，展开后隐藏 */
.custom-expander:not([open]) .custom-expander-summary .cluster-card{
  display: block;
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 14px;
  padding: 10px 14px 8px 14px;
  box-shadow: 0 8px 20px rgba(0,0,0,.25);
  margin-bottom: 4px;
}
.custom-expander[open] .custom-expander-summary .cluster-card{
  display: none;
}
/* Details包装器：展开后显示 */
.details-wrapper{
  position: relative;
  margin-top: 4px;
}
/* Sticky卡片：固定在最顶部 */
.cluster-card-sticky{
  position: sticky !important;
  top: 0 !important;
  z-index: 100 !important;
  background: linear-gradient(180deg, rgba(15,23,42,1) 0%, rgba(15,23,42,0.98) 85%, rgba(15,23,42,0.7) 100%) !important;
  padding-bottom: 6px;
  margin-bottom: 0;
}
.cluster-card-sticky .cluster-card{
  background: linear-gradient(145deg, rgba(18,26,49,.92), rgba(15,23,42,.92));
  border: 1px solid rgba(148,163,184,.16);
  border-radius: 14px;
  padding: 10px 14px 8px 14px;
  box-shadow: 0 8px 20px rgba(0,0,0,.25);
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
  padding-bottom: 400px; /* 底部留白，让最后的讨论点也能滚动到顶部 */
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
  border-radius: 10px;
  padding: 5px 12px;
  margin: 6px 10px;
  text-align: left;
  color: var(--text);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.expander-toggle-inside:hover{
  background: rgba(15,23,42,.9);
}
.expander-toggle-inside .toggle-icon{
  display: inline-block;
  margin-right: 6px;
  font-size: 0.7rem;
}
.expander-toggle-inside .toggle-text{
  font-size: 0.85rem;
}
/* 底部收起按钮 */
.expander-toggle-bottom{
  background: linear-gradient(145deg, rgba(236,72,153,.12), rgba(139,92,246,.08));
  border: 1px solid rgba(236,72,153,.25);
  border-radius: 10px;
  padding: 8px 16px;
  margin: 12px 10px 6px 10px;
  text-align: center;
  color: #ec4899;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.expander-toggle-bottom:hover{
  background: linear-gradient(145deg, rgba(236,72,153,.20), rgba(139,92,246,.15));
  border-color: rgba(236,72,153,.4);
}
.expander-toggle-bottom .toggle-icon{
  display: inline-block;
  margin-right: 6px;
  font-size: 0.7rem;
}
.expander-toggle-bottom .toggle-text{
  font-size: 0.9rem;
}
.custom-expander{
  border-radius: 14px;
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
  border-radius: 14px;
  padding: 6px 14px;
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
  padding: 8px 12px;
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

/* 讨论点可展开卡片 */
.dp-expander{
  margin: 6px 0;
  border-radius: 10px;
}
.dp-expander-summary{
  list-style: none;
  cursor: pointer;
  user-select: none;
}
.dp-expander-summary::-webkit-details-marker{
  display: none;
}
.dp-card{
  background: linear-gradient(145deg, rgba(236,72,153,.12), rgba(139,92,246,.08));
  border: 1px solid rgba(236,72,153,.22);
  border-radius: 10px;
  padding: 8px 12px;
  transition: all 0.2s ease;
}
.dp-card:hover{
  background: linear-gradient(145deg, rgba(236,72,153,.18), rgba(139,92,246,.12));
  border-color: rgba(236,72,153,.35);
}
.dp-header{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.dp-title{
  font-weight: 800;
  font-size: 1.2rem;
  color: #fff;
  flex: 1;
}
.dp-toggle-btn{
  font-size: 0.72rem;
  font-weight: 600;
  color: #ec4899;
  background: rgba(236,72,153,.15);
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(236,72,153,.3);
  transition: all 0.2s ease;
  white-space: nowrap;
}
.dp-card:hover .dp-toggle-btn{
  background: rgba(236,72,153,.25);
  border-color: rgba(236,72,153,.5);
  color: #f472b6;
}
.dp-toggle-btn .expand-text{ display: inline; }
.dp-toggle-btn .collapse-text{ display: none; }
.dp-expander[open] .dp-toggle-btn{
  background: rgba(236,72,153,.3);
}
.dp-expander[open] .dp-toggle-btn .expand-text{ display: none; }
.dp-expander[open] .dp-toggle-btn .collapse-text{ display: inline; }
/* 展开后隐藏summary中的卡片 */
.dp-expander[open] .dp-expander-summary .dp-card{
  display: none;
}
/* 讨论点详情包装器 */
.dp-details-wrapper{
  position: relative;
  border: 1px solid rgba(236,72,153,.22);
  border-radius: 10px;
  overflow: hidden;
}
/* 讨论点Sticky卡片 */
.dp-card-sticky{
  position: sticky;
  top: 0;
  z-index: 50;
  background: linear-gradient(180deg, rgba(15,23,42,1) 0%, rgba(15,23,42,0.98) 90%, rgba(15,23,42,0.8) 100%);
  padding-bottom: 4px;
}
.dp-card-sticky .dp-card{
  background: linear-gradient(145deg, rgba(236,72,153,.15), rgba(139,92,246,.10));
  border: 1px solid rgba(236,72,153,.28);
  border-radius: 10px;
  margin: 0;
  cursor: pointer;
  transition: all 0.2s ease;
}
.dp-card-sticky .dp-card:hover{
  background: linear-gradient(145deg, rgba(236,72,153,.22), rgba(139,92,246,.15));
  border-color: rgba(236,72,153,.4);
}
/* 讨论点内容区域（自适应高度，无需滚动） */
.dp-scrollable{
  overflow: visible;
}
/* 讨论点收起按钮 */
.dp-collapse-btn{
  background: rgba(236,72,153,.12);
  border: 1px solid rgba(236,72,153,.2);
  border-radius: 8px;
  padding: 6px 12px;
  margin: 8px 10px;
  text-align: left;
  color: #ec4899;
  font-weight: 600;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.dp-collapse-btn:hover{
  background: rgba(236,72,153,.2);
}
.dp-content{
  background: rgba(15,23,42,.4);
  padding: 10px 12px;
}

/* ===== 讨论点直接展示样式（不折叠）===== */
.dp-card-wrapper{
  background: linear-gradient(145deg, rgba(236,72,153,.08), rgba(139,92,246,.05));
  border: 1px solid rgba(236,72,153,.20);
  border-radius: 12px;
  margin: 10px 0;
  overflow: hidden;
}
.dp-card-header-fixed{
  background: linear-gradient(145deg, rgba(236,72,153,.15), rgba(139,92,246,.10));
  border-bottom: 1px solid rgba(236,72,153,.18);
  padding: 10px 14px;
}
.dp-card-header-fixed .dp-title{
  font-weight: 800;
  font-size: 1.2rem;
  color: #fff;
}
.dp-content-direct{
  background: rgba(15,23,42,.35);
  padding: 12px 14px;
}

.dp-section-title{
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text);
  margin: 8px 0 6px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.dp-section-title:first-child{
  margin-top: 0;
}

.opinion-item{
  background: rgba(34,211,238,.10);
  border: 1px solid rgba(34,211,238,.16);
  padding: 6px 10px;
  margin: 4px 0;
  border-radius: 8px;
  color: var(--text);
  font-size: 1.05rem;
  line-height: 1.6;
}
.example-quote{
  background: rgba(99,102,241,.10);
  border: 1px solid rgba(99,102,241,.16);
  padding: 5px 10px;
  margin: 3px 0;
  border-radius: 8px;
  color: #c7d2fe;
  font-style: italic;
  font-size: 0.88rem;
  line-height: 1.5;
}

/* ===== 新增：观点卡片样式（V2格式）===== */
.opinion-card{
  background: rgba(34,211,238,.08);
  border: 1px solid rgba(34,211,238,.18);
  border-radius: 10px;
  padding: 12px 14px;
  margin: 10px 0;
}
.opinion-card-header{
  font-size: 1.12rem;
  font-weight: 700;
  color: #22d3ee;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.4;
}
.opinion-card-content{
  margin-left: 4px;
}

/* 原文发言展开器 */
.raw-msg-expander{
  margin-top: 8px;
  border-radius: 8px;
}
.raw-msg-summary{
  list-style: none;
  cursor: pointer;
  user-select: none;
  background: rgba(251,146,60,.12);
  border: 1px solid rgba(251,146,60,.22);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fb923c;
  transition: all 0.2s ease;
}
.raw-msg-summary::-webkit-details-marker{
  display: none;
}
.raw-msg-summary:hover{
  background: rgba(251,146,60,.18);
  border-color: rgba(251,146,60,.35);
}
.raw-msg-expander[open] .raw-msg-summary{
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
.raw-msg-content{
  background: rgba(251,146,60,.06);
  border: 1px solid rgba(251,146,60,.18);
  border-top: none;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  padding: 8px 10px;
  max-height: 300px;
  overflow-y: auto;
}
.raw-msg-item{
  background: rgba(15,23,42,.5);
  border: 1px solid rgba(148,163,184,.12);
  border-radius: 6px;
  padding: 6px 10px;
  margin: 4px 0;
  font-size: 0.88rem;
  line-height: 1.5;
}
.raw-msg-item .msg-meta{
  color: var(--muted);
  font-size: 0.78rem;
  margin-bottom: 2px;
}
.raw-msg-item .msg-content{
  color: var(--text);
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
  padding: 8px 5% 16px;
  background: linear-gradient(to bottom, rgba(168, 85, 247, 0.1), transparent);
  text-align: center;
}
.logo-group{
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
}
.title-stack{
  text-align: left;
}
.title-stack h1{
  margin: 0;
  font-size: 2.8rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: white;
}
.title-stack h1 .title-icon{
  -webkit-text-fill-color: initial;
  background: none;
}
.title-stack h1 span:not(.title-icon){
  background: linear-gradient(to right, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.status-badges{
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  margin-top: 10px;
}
.badge{
  font-size: 0.9rem;
  padding: 6px 14px;
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
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
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
  font-size: 1rem;
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
  font-size: 1.1rem;
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
  font-size: 2.2rem;
  margin-bottom: 16px;
  display: block;
}
.intro-card h3{ margin: 0 0 10px; font-size: 1.25rem; font-weight: 700; color: white; }
.intro-card p{ color: var(--text-dim); font-size: 1.05rem; line-height: 1.6; margin: 0; }
.intro-card:hover{
  background: rgba(255,255,255,0.05);
  transform: translateY(-5px);
  border-color: var(--accent-primary);
}

/* Homepage Tabs Styling */
.stTabs [data-baseweb="tab-list"]{
  display: flex !important;
  gap: 8px;
  background: transparent !important;
  padding: 4px;
  border-radius: 12px;
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 auto 20px;
  border: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
}
.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"]{
  display: none !important;
}
/* Tab按钮基础样式 */
div[data-baseweb="tab-list"] button[role="tab"],
.stTabs [data-baseweb="tab"],
button[data-baseweb="tab"]{
  flex: 1 1 0% !important;
  min-width: 0 !important;
  height: auto !important;
  padding: 14px 24px !important;
  background: rgba(0,0,0,0.4) !important;
  border-radius: 12px !important;
  color: var(--text-dim) !important;
  font-weight: 800 !important;
  font-size: 1.5rem !important;
  justify-content: center !important;
  text-align: center !important;
  border: 2px solid var(--glass-border) !important;
  letter-spacing: 0.03em !important;
  transition: all 0.25s ease !important;
}
/* Tab按钮内部文字 */
div[data-baseweb="tab-list"] button[role="tab"] p,
div[data-baseweb="tab-list"] button[role="tab"] span,
.stTabs button p,
.stTabs button span{
  font-size: 1.5rem !important;
  font-weight: 800 !important;
  color: inherit !important;
}
div[data-baseweb="tab-list"] button[role="tab"]:hover,
.stTabs [data-baseweb="tab"]:hover,
button[data-baseweb="tab"]:hover{
  background: rgba(168,85,247,0.2) !important;
  border-color: rgba(168,85,247,0.5) !important;
}
/* Tab按钮选中状态 */
div[data-baseweb="tab-list"] button[aria-selected="true"],
.stTabs [aria-selected="true"],
button[aria-selected="true"]{
  background: linear-gradient(135deg, rgba(168,85,247,0.4), rgba(139,92,246,0.3)) !important;
  color: white !important;
  border-color: #a855f7 !important;
  box-shadow: 0 8px 24px rgba(168, 85, 247, 0.4) !important;
  text-shadow: 0 0 12px rgba(168, 85, 247, 0.6) !important;
}
.stTabs [aria-selected="true"]::after{
  display: none !important;
}
.stTabs [data-baseweb="tab-panel"]{
  padding: 16px 0 !important;
}
/* 隐藏 tabs 底部横线 */
.stTabs{
  display: flex !important;
  justify-content: center !important;
}
.stTabs > div:first-child{
  background: transparent !important;
  width: 100% !important;
  margin: 0 auto !important;
}
.stTabs > div > div:first-child{
  background: transparent !important;
  border: none !important;
  width: 100% !important;
}
.stTabs [role="tablist"]{
  background: transparent !important;
  gap: 8px !important;
  width: 100% !important;
}
.stTabs [role="tablist"]::before,
.stTabs [role="tablist"]::after{
  display: none !important;
}

/* 主查询卡片 - 标题样式 */
.query-card-header{
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(168, 85, 247, 0.25);
  letter-spacing: 0.05em;
  position: relative;
}
/* emoji 图标 - 保持原色 */
.query-card-header .header-icon{
  font-size: 1.5rem;
  display: inline-block;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}
/* 文字部分 - 应用渐变色 */
.query-card-header .header-text{
  background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #e879f9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  letter-spacing: 0.05em;
  filter: drop-shadow(0 0 8px rgba(168, 85, 247, 0.2));
}

/* ===== Tooltip 悬停提示样式（Streamlit 兼容）===== */
/* 确保父容器不会裁剪 tooltip */
.cluster-meta{
  overflow: visible !important;
}
.meta-chip.time-chip{
  position: relative !important;
  overflow: visible !important;
  cursor: pointer;
  transition: all 0.2s ease;
}
.meta-chip.time-chip:hover{
  background: rgba(236, 72, 153, 0.18);
  border-color: rgba(236, 72, 153, 0.35);
}
.time-tooltip-wrapper{
  position: relative !important;
  display: inline-block;
  cursor: pointer;
  overflow: visible !important;
}
.time-tooltip-wrapper .tooltip-content{
  visibility: hidden;
  opacity: 0;
  position: absolute !important;
  bottom: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%) translateY(5px);
  background: linear-gradient(145deg, rgba(18, 26, 49, 0.98), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(236, 72, 153, 0.35);
  border-radius: 12px;
  padding: 12px 16px;
  min-width: 280px;
  max-width: 450px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45), 0 0 20px rgba(236, 72, 153, 0.15);
  z-index: 99999 !important;
  transition: opacity 0.25s ease, visibility 0.25s ease, transform 0.25s ease;
  white-space: normal;
  word-break: break-all;
  line-height: 1.5;
  /* 允许鼠标与 tooltip 交互 */
  pointer-events: auto;
  cursor: default;
}
/* 桥接区域：填充 tooltip 和触发元素之间的间隙，防止鼠标移动时窗口消失 */
.time-tooltip-wrapper .tooltip-content::before{
  content: '';
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  height: 20px; /* 覆盖间隙区域 */
  background: transparent;
}
/* 小三角箭头 */
.time-tooltip-wrapper .tooltip-content::after{
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(18, 26, 49, 0.98);
  z-index: 1;
}
.time-tooltip-wrapper .tooltip-content .tooltip-title{
  font-size: 0.78rem;
  font-weight: 700;
  color: #ec4899;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.time-tooltip-wrapper .tooltip-content .tooltip-text{
  font-size: 0.88rem;
  color: #e5e7eb;
  /* 允许选择文本 */
  user-select: text;
  cursor: text;
}
/* 触发显示：鼠标悬停在触发元素上 */
.time-tooltip-wrapper:hover .tooltip-content{
  visibility: visible;
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
/* 保持显示：鼠标悬停在 tooltip 窗口上时也保持显示 */
.time-tooltip-wrapper .tooltip-content:hover{
  visibility: visible;
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
/* 悬停时的高亮效果 */
.time-tooltip-wrapper:hover{
  color: #f472b6;
}

/* 主页查询区域 - 所有标签字体放大 */
section[data-testid="stMain"] label,
section[data-testid="stMain"] [data-testid="stWidgetLabel"] label,
section[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
section[data-testid="stMain"] .stSelectbox label,
section[data-testid="stMain"] .stDateInput label,
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] p,
.stSelectbox [data-testid="stWidgetLabel"],
.stDateInput [data-testid="stWidgetLabel"]{
  font-size: 1.4rem !important;
  font-weight: 800 !important;
  color: #e9d5ff !important;
  margin-bottom: 10px !important;
  letter-spacing: 0.02em !important;
}

/* Streamlit label 内部的 p 标签 */
[data-testid="stWidgetLabel"] p{
  font-size: 1.4rem !important;
  font-weight: 800 !important;
  color: #e9d5ff !important;
}

/* 主页查询区域 - 下拉框宽度缩短 */
section[data-testid="stMain"] [data-testid="stSelectbox"]{
  max-width: 350px !important;
}
section[data-testid="stMain"] [data-testid="stDateInput"]{
  max-width: 350px !important;
}

/* 查询区域容器样式 - 通过标记ID定位 */
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] > .query-card-header){
  background: rgba(15, 23, 42, 0.85) !important;
  border: 2px solid var(--accent-primary) !important;
  border-radius: 20px !important;
  padding: 20px 24px !important;
  margin-bottom: 20px !important;
  box-shadow: 0 15px 40px rgba(168, 85, 247, 0.2) !important;
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

    local_path = LOCAL_RESULTS_DIR / group["dir"] / "daily" / f"{date}.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/daily/{date}.json"
        data = fetch_json(url)
        return data or {}
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return {}

@st.cache_data(ttl=300, show_spinner=False)
def load_version_info(group_id: str, version_key: str) -> dict:
    """快速加载版本的基本信息（名称和周期）用于显示"""
    group = GROUPS.get(group_id)
    if not group:
        return {"version": version_key, "period": ""}

    local_path = LOCAL_RESULTS_DIR / group["dir"] / "version" / f"{version_key}.json"
    if local_path.exists():
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "version": data.get("version", version_key),
                    "period": data.get("period", "")
                }
        except:
            pass

    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/version/{version_key}.json"
        data = fetch_json(url)
        if data:
            return {
                "version": data.get("version", version_key),
                "period": data.get("period", "")
            }
    except:
        pass
    
    return {"version": version_key, "period": ""}

def load_version_result(group_id: str, version_key: str) -> dict:
    """加载版本分析数据"""
    group = GROUPS.get(group_id)
    if not group:
        return {}

    local_path = LOCAL_RESULTS_DIR / group["dir"] / "version" / f"{version_key}.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        url = f"{GITHUB_RAW_BASE}/{group['dir']}/version/{version_key}.json"
        data = fetch_json(url)
        return data or {}
    except Exception as e:
        st.error(f"加载版本数据失败: {e}")
        return {}


# ==================== 构建讨论点内容HTML（支持新旧格式）====================

def build_discussion_point_html(dp: dict, dp_i: int, group_key: str, date: str, cluster_idx: int) -> str:
    """
    构建单个讨论点的HTML内容
    支持新格式（观点列表）和旧格式（玩家观点数组）
    """
    # 找到讨论点标题
    dp_title = ""
    for k in dp.keys():
        if str(k).startswith("讨论点"):
            dp_title = (dp.get(k) or "").strip()
            break
    
    dp_inner_html = ""
    
    # 检查是否为新格式（有观点列表）
    opinion_list = dp.get("观点列表", [])
    
    if opinion_list:
        # ===== 新格式：观点列表 =====
        for op_idx, opinion_obj in enumerate(opinion_list, 1):
            # 找到观点标题（玩家观点1、玩家观点2 等）
            opinion_title = ""
            for k in opinion_obj.keys():
                if str(k).startswith("玩家观点"):
                    opinion_title = opinion_obj.get(k, "")
                    break
            
            # 代表性玩家发言
            rep_quotes = opinion_obj.get("代表性玩家发言", []) or []
            
            # 原文发言
            raw_messages = opinion_obj.get("原文发言", []) or []
            
            # 构建观点卡片
            dp_inner_html += f'<div class="opinion-card">'
            dp_inner_html += f'<div class="opinion-card-header">💭 观点{op_idx}：{html.escape(opinion_title)}</div>'
            dp_inner_html += '<div class="opinion-card-content">'
            
            # 代表性发言
            if rep_quotes:
                dp_inner_html += '<div class="dp-section-title">📝 代表性发言</div>'
                for quote in rep_quotes:
                    dp_inner_html += f'<div class="example-quote">{html.escape(quote)}</div>'
            
            # 原文发言（可展开）
            if raw_messages:
                raw_msg_id = f"raw-{group_key or 'g'}-{date}-{cluster_idx}-{dp_i}-{op_idx}"
                dp_inner_html += f'''<details class="raw-msg-expander" id="{raw_msg_id}">
<summary class="raw-msg-summary">📋 查看原文发言（{len(raw_messages)} 条）▼</summary>
<div class="raw-msg-content">'''
                
                for msg in raw_messages:
                    msg_date = msg.get("发言日期", "")
                    msg_time = msg.get("发言时间", "")
                    msg_player = msg.get("玩家ID", "")
                    msg_content = msg.get("玩家消息", "")
                    
                    dp_inner_html += f'''<div class="raw-msg-item">
<div class="msg-meta">{html.escape(msg_date)} {html.escape(msg_time)} | {html.escape(msg_player)}</div>
<div class="msg-content">{html.escape(msg_content)}</div>
</div>'''
                
                dp_inner_html += '</div></details>'
            
            dp_inner_html += '</div></div>'
    
    else:
        # ===== 旧格式：玩家观点数组 + 代表性玩家发言示例 =====
        opinions = dp.get("玩家观点", []) or []
        examples = dp.get("代表性玩家发言示例", []) or []
        
        if opinions:
            dp_inner_html += '<div class="dp-section-title">💭 玩家观点</div>'
            for opinion in opinions:
                dp_inner_html += f'<div class="opinion-item">{html.escape(opinion)}</div>'
        
        if examples:
            dp_inner_html += f'<div class="dp-section-title">📝 代表性发言</div>'
            for example in examples:
                dp_inner_html += f'<div class="example-quote">"{html.escape(example)}"</div>'
    
    if not dp_inner_html:
        dp_inner_html = '<p style="color: var(--muted); font-size: 0.85rem; margin: 0;">暂无详细内容</p>'
    
    # 生成讨论点卡片（直接展示，不折叠）
    dp_id = f"dp-{group_key or 'g'}-{date}-{cluster_idx}-{dp_i}"
    dp_title_escaped = html.escape(dp_title) if dp_title else f"讨论点 {dp_i}"
    
    return f'''<div class="dp-card-wrapper" id="{dp_id}">
<div class="dp-card-header-fixed">
<span class="dp-title">📌 {dp_i}. {dp_title_escaped}</span>
</div>
<div class="dp-content-direct">
{dp_inner_html}
</div>
</div>'''


# ==================== 渲染 ====================

def render_result(result: dict, group_key: str | None = None, available_dates: list | None = None):
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
    
    # 报告标题（居中显示，无卡片背景，贴顶）
    st.markdown(
        f"""<div style="text-align: center; padding: 0 0 1rem 0; margin-top: -4rem;">
<h1 style="margin: 0; color: #e9d5ff; font-size: 2rem; font-weight: 700;">
📊 {platform_display} {group_display} {formatted_date} 分析报告 <span style="color: #fbbf24;">_热门讨论TOP5</span>
</h1>
</div>""",
        unsafe_allow_html=True,
    )

    # ========= 热门话题列表（摘要卡 + 展开详情）=========
    sorted_clusters = sorted(clusters, key=lambda x: float(x.get("热度评分", 0) or 0), reverse=True)

    # 添加JavaScript：每次渲染时强制关闭所有展开的details元素
    reset_key = f"{group_key or 'g'}-{date}"
    components.html(f"""
<script>
(function() {{
    function closeAllExpanders() {{
        var allDetails = window.parent.document.querySelectorAll('details.custom-expander[open]');
        allDetails.forEach(function(d) {{
            d.removeAttribute('open');
        }});
    }}
    closeAllExpanders();
    setTimeout(closeAllExpanders, 100);
    setTimeout(closeAllExpanders, 300);
}})();
</script>
<div style="display:none;" data-reset-key="{reset_key}"></div>
""", height=0)

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
            full_time_escaped = html.escape(time_axis)
            if len(time_axis) <= 70:
                meta_chips.append(f'<div class="meta-chip"><span>⏰ 时间</span>{full_time_escaped}</div>')
            else:
                short_time = html.escape(time_axis[:70] + "…")
                meta_chips.append(f'''<div class="meta-chip time-chip">
<div class="time-tooltip-wrapper">
<span>⏰ 时间</span>{short_time}
<div class="tooltip-content">
<div class="tooltip-title">📅 完整时间轴</div>
<div class="tooltip-text">{full_time_escaped}</div>
</div>
</div>
</div>''')

        # 构建讨论点内容HTML
        discussion_content_html = ""
        
        discussion_list = cluster.get("讨论点列表", []) or []
        
        if discussion_list:
            discussion_content_html += f'<div style="color: #e9d5ff; font-size: 1.05rem; margin-bottom: 10px; font-weight: 700;">💬 讨论点（共 {len(discussion_list)} 条）</div>'
            
            for dp_i, dp in enumerate(discussion_list, 1):
                discussion_content_html += build_discussion_point_html(dp, dp_i, group_key, date, idx)
        else:
            discussion_content_html = '<p style="color: var(--muted);">暂无讨论点列表</p>'
        
        # 渲染完整的自定义HTML
        title_escaped = html.escape(title)
        unique_id = f"cluster-{group_key or 'g'}-{date}-{idx}"
        
        st.markdown(
            f"""<div class="cluster-custom-wrapper">
<details class="custom-expander" id="{unique_id}">
<summary class="custom-expander-summary">
<div class="cluster-card" style="position: relative;">
<div class="cluster-header">
<div>
<div class="cluster-title">{idx}. {title_escaped}</div>
<div class="cluster-meta">{''.join(meta_chips)}</div>
</div>
<div class="badge-heat"><small>热度</small>{heat:.1f} 🔥</div>
</div>
<div style="position: absolute; right: 14px; bottom: 10px; font-size: 0.85rem; font-weight: 700; color: #ec4899;">点击查看详情</div>
</div>
</summary>
<div class="details-wrapper">
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
<div class="scrollable-content">
<div class="custom-expander-inner">
{discussion_content_html}
</div>
<div class="expander-toggle-bottom">
<span class="toggle-icon">▲</span>
<span class="toggle-text">点击收起</span>
</div>
</div>
</div>
</details>
</div>""",
            unsafe_allow_html=True,
        )

    # ========= JavaScript：处理收起详情按钮 =========
    components.html(
        """
<script>
(function() {
    function setupCollapseButtons() {
        const parentDoc = window.parent.document;
        
        const collapseButtons = parentDoc.querySelectorAll('.expander-toggle-inside');
        
        collapseButtons.forEach((button, index) => {
            if (button.dataset.bound === 'true') {
                return;
            }
            button.dataset.bound = 'true';
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
        
        const dpStickyCards = parentDoc.querySelectorAll('.dp-card-sticky');
        
        dpStickyCards.forEach((card, index) => {
            if (card.dataset.dpbound === 'true') {
                return;
            }
            card.dataset.dpbound = 'true';
            
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details.dp-expander');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                }
            });
        });
        
        // 话题簇顶部sticky卡片点击收起
        const clusterStickyCards = parentDoc.querySelectorAll('.cluster-card-sticky');
        
        clusterStickyCards.forEach((card) => {
            if (card.dataset.clusterbound === 'true') {
                return;
            }
            card.dataset.clusterbound = 'true';
            
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details.custom-expander');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
        
        // 底部收起按钮点击收起
        const bottomButtons = parentDoc.querySelectorAll('.expander-toggle-bottom');
        
        bottomButtons.forEach((button) => {
            if (button.dataset.bottombound === 'true') {
                return;
            }
            button.dataset.bottombound = 'true';
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
    }
    
    setTimeout(setupCollapseButtons, 100);
    setTimeout(setupCollapseButtons, 300);
    setTimeout(setupCollapseButtons, 500);
    setTimeout(setupCollapseButtons, 800);
    setTimeout(setupCollapseButtons, 1200);
    setTimeout(setupCollapseButtons, 2000);
    
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
    
    # ========= 日期导航 =========
    if available_dates and date:
        from datetime import timedelta
        
        try:
            current_date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            current_date_obj = None
        
        if current_date_obj:
            prev_date_obj = current_date_obj - timedelta(days=1)
            next_date_obj = current_date_obj + timedelta(days=1)
            
            prev_date_str = prev_date_obj.strftime("%Y-%m-%d")
            next_date_str = next_date_obj.strftime("%Y-%m-%d")
            
            prev_display = prev_date_obj.strftime("%Y-%m-%d")
            next_display = next_date_obj.strftime("%Y-%m-%d")
            current_display = current_date_obj.strftime("%Y-%m-%d")
            
            has_prev = prev_date_str in available_dates
            has_next = next_date_str in available_dates
            
            st.markdown("---")
            st.markdown("### 📅 日期导航")
            
            # 三等宽列，按钮占满列宽
            nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1], gap="large")
            
            with nav_col1:
                if has_prev:
                    if st.button(f"◀ {prev_display}", key="nav_prev", use_container_width=True):
                        st.session_state.confirmed_date = prev_date_str
                        st.session_state.selected_date_cache = prev_date_str
                        st.rerun()
                else:
                    st.button(f"◀ {prev_display}", key="nav_prev_disabled", use_container_width=True, disabled=True)
            
            with nav_col2:
                st.markdown(
                    f"""<div style="text-align: center; padding: 0.5rem 1rem; background: rgba(168,85,247,0.25); 
                    border-radius: 8px; border: 2px solid rgba(168,85,247,0.5);">
                    <span style="font-size: 1.45rem; font-weight: 700; color: #e9d5ff;">📅 {current_display}</span>
                    </div>""",
                    unsafe_allow_html=True
                )
            
            with nav_col3:
                if has_next:
                    if st.button(f"{next_display} ▶", key="nav_next", use_container_width=True):
                        st.session_state.confirmed_date = next_date_str
                        st.session_state.selected_date_cache = next_date_str
                        st.rerun()
                else:
                    st.button(f"{next_display} ▶", key="nav_next_disabled", use_container_width=True, disabled=True)
    
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

                    # 支持新格式
                    opinion_list = dp.get("观点列表", [])
                    if opinion_list:
                        for op_idx, opinion_obj in enumerate(opinion_list, 1):
                            opinion_title = ""
                            for k in opinion_obj.keys():
                                if str(k).startswith("玩家观点"):
                                    opinion_title = opinion_obj.get(k, "")
                                    break
                            report_lines.append(f"**观点{op_idx}**: {opinion_title}\n\n")
                            
                            rep_quotes = opinion_obj.get("代表性玩家发言", []) or []
                            if rep_quotes:
                                report_lines.append("代表性发言:\n")
                                for quote in rep_quotes:
                                    report_lines.append(f'> {quote}\n')
                                report_lines.append("\n")
                    else:
                        # 旧格式
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

def render_version_result(result: dict, group_key: str | None = None):
    """渲染版本分析结果页面"""
    if not result:
        st.warning("⚠️ 暂无版本数据")
        return

    version = result.get("version", "")
    period = result.get("period", "")
    topics = result.get("topics", [])

    # 群名称格式化
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
            group_display = cleaned_name + " "

    # 获取平台信息
    platform = result.get("source", "QQ")
    platform_display = {
        "QQ": "QQ",
        "微信": "微信",
        "WeChat": "微信",
        "Discord": "Discord"
    }.get(platform, platform)
    
    # 报告标题（一行显示）
    st.markdown(
        f"""<div style="text-align: center; padding: 0 0 1.5rem 0; margin-top: -4rem;">
<h1 style="margin: 0; color: #e9d5ff; font-size: 1.8rem; font-weight: 700; white-space: nowrap;">
📊 {platform_display} {group_display}{version} ({period})_热门讨论TOP{len(topics)}
</h1>
</div>""",
        unsafe_allow_html=True,
    )

    for topic in topics:
        rank = topic.get("rank", 0)
        title = topic.get("title", "(未命名话题)")
        heat = topic.get("heat_score", 0)
        days = topic.get("discussion_days", 0)
        date_range = topic.get("date_range", "")
        players = topic.get("total_players", 0)
        msgs = topic.get("total_messages", 0)
        heat_trend = topic.get("heat_trend", "")
        discussion_points = topic.get("discussion_points", [])

        title_escaped = html.escape(title)
        heat_trend_escaped = html.escape(heat_trend)
        
        # 构建讨论点内容
        discussion_content_html = ""
        if discussion_points:
            discussion_content_html += f'<div style="color: #e9d5ff; font-size: 1.05rem; margin-bottom: 10px; font-weight: 700;">📋 核心讨论点（共 {len(discussion_points)} 条）</div>'
            
            for dp_i, dp in enumerate(discussion_points, 1):
                dp_title = dp.get("point", "")
                opinions = dp.get("opinions", [])
                examples = dp.get("examples", [])
                
                dp_inner_html = ""
                
                if opinions:
                    dp_inner_html += '<div class="dp-section-title">💭 玩家观点</div>'
                    for i, opinion in enumerate(opinions, 1):
                        dp_inner_html += f'<div class="opinion-item">{i}. {html.escape(opinion)}</div>'
                
                if examples:
                    dp_inner_html += f'<div class="dp-section-title">📝 代表性发言</div>'
                    for example in examples:
                        dp_inner_html += f'<div class="example-quote">"{html.escape(example)}"</div>'
                
                if not dp_inner_html:
                    dp_inner_html = '<p style="color: var(--muted); font-size: 0.85rem; margin: 0;">暂无详细内容</p>'
                
                dp_id = f"vdp-{group_key or 'g'}-{version}-{rank}-{dp_i}"
                dp_title_escaped = html.escape(dp_title) if dp_title else f"讨论点 {dp_i}"
                
                discussion_content_html += f'''<details class="dp-expander" id="{dp_id}">
<summary class="dp-expander-summary">
<div class="dp-card">
<div class="dp-header">
<span class="dp-title">📌 {dp_i}. {dp_title_escaped}</span>
<span class="dp-toggle-btn"><span class="expand-text">展开 ▼</span><span class="collapse-text">收起 ▲</span></span>
</div>
</div>
</summary>
<div class="dp-details-wrapper">
<div class="dp-card-sticky">
<div class="dp-card">
<div class="dp-header">
<span class="dp-title">📌 {dp_i}. {dp_title_escaped}</span>
<span class="dp-toggle-btn"><span class="collapse-text">收起 ▲</span></span>
</div>
</div>
</div>
<div class="dp-scrollable">
<div class="dp-content">
{dp_inner_html}
</div>
</div>
</div>
</details>'''
        else:
            discussion_content_html = '<p style="color: var(--muted);">暂无讨论点列表</p>'
        
        unique_id = f"vtopic-{group_key or 'g'}-{version}-{rank}"
        
        st.markdown(
            f"""<div class="cluster-custom-wrapper">
<details class="custom-expander" id="{unique_id}">
<summary class="custom-expander-summary">
<div class="cluster-card">
<div class="cluster-header">
<div style="flex: 1;">
<div class="cluster-title">{rank}. {title_escaped}</div>
</div>
<div style="display: flex; gap: 12px; align-items: center;">
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
<div style="font-size: 1.5rem; font-weight: 800; color: #c7d2fe;">{players}</div>
<div style="font-size: 0.75rem; color: var(--muted);">参与玩家</div>
</div>
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
<div style="font-size: 1.5rem; font-weight: 800; color: #c7d2fe;">{msgs}</div>
<div style="font-size: 0.75rem; color: var(--muted);">发言数</div>
</div>
<div class="badge-heat"><small>热度</small>{heat:.2f} 🔥</div>
</div>
</div>

<div style="margin-top: 12px; margin-bottom: 12px;">
<div style="display: inline-block; background: rgba(59,130,246,0.15); color: #60a5fa; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; margin-bottom: 0;">热度趋势</div>
<div style="font-size: 0.88rem; color: var(--text); line-height: 1.6;">{heat_trend_escaped}</div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
<div style="font-size: 0.85rem; color: var(--muted);">{date_range} · 持续 {days} 天</div>
<div style="font-size: 0.85rem; font-weight: 700; color: #ec4899; cursor: pointer;">点击查看详情</div>
</div>
</div>
</summary>
<div class="details-wrapper">
<div class="cluster-card-sticky">
<div class="cluster-card">
<div class="cluster-header">
<div style="flex: 1;">
<div class="cluster-title">{rank}. {title_escaped}</div>
<div class="cluster-meta">
<div class="meta-chip"><span>📅</span>{days}天</div>
<div class="meta-chip"><span>👥</span>{players}人</div>
<div class="meta-chip"><span>💬</span>{msgs}条</div>
</div>
</div>
<div class="badge-heat"><small>热度</small>{heat:.2f} 🔥</div>
</div>
</div>
</div>
<div class="scrollable-content">
<div class="custom-expander-inner">
{discussion_content_html}
</div>
<div class="expander-toggle-bottom">
<span class="toggle-icon">▲</span>
<span class="toggle-text">点击收起</span>
</div>
</div>
</div>
</details>
</div>""",
            unsafe_allow_html=True,
        )
    
    # 版本分析页面的JavaScript
    components.html("""
<script>
(function() {
    function setupVersionCollapseButtons() {
        const parentDoc = window.parent.document;
        
        const collapseButtons = parentDoc.querySelectorAll('.expander-toggle-inside');
        
        collapseButtons.forEach((button) => {
            if (button.dataset.vbound === 'true') {
                return;
            }
            button.dataset.vbound = 'true';
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
        
        const dpStickyCards = parentDoc.querySelectorAll('.dp-card-sticky');
        
        dpStickyCards.forEach((card) => {
            if (card.dataset.vdpbound === 'true') {
                return;
            }
            card.dataset.vdpbound = 'true';
            
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details.dp-expander');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
        
        // 话题簇顶部sticky卡片点击收起
        const clusterStickyCards = parentDoc.querySelectorAll('.cluster-card-sticky');
        
        clusterStickyCards.forEach((card) => {
            if (card.dataset.vclusterbound === 'true') {
                return;
            }
            card.dataset.vclusterbound = 'true';
            
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details.custom-expander');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
        
        // 底部收起按钮点击收起
        const bottomButtons = parentDoc.querySelectorAll('.expander-toggle-bottom');
        
        bottomButtons.forEach((button) => {
            if (button.dataset.vbottombound === 'true') {
                return;
            }
            button.dataset.vbottombound = 'true';
            
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const details = this.closest('details');
                if (details) {
                    details.open = false;
                    details.removeAttribute('open');
                    
                    details.style.display = 'none';
                    details.offsetHeight;
                    details.style.display = '';
                    
                    setTimeout(() => {
                        details.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 50);
                }
            });
        });
    }
    
    setupVersionCollapseButtons();
    setTimeout(setupVersionCollapseButtons, 100);
    setTimeout(setupVersionCollapseButtons, 300);
    setTimeout(setupVersionCollapseButtons, 500);
    setTimeout(setupVersionCollapseButtons, 800);
    setTimeout(setupVersionCollapseButtons, 1200);
})();
</script>
""", height=0)

# ==================== 自定义日历选择器 ====================

def render_custom_calendar(available_dates: list, current_date: str, key_prefix: str = "cal"):
    """
    渲染紧凑型自定义日历选择器（类似原生date_input样式）
    """
    import calendar
    
    if not available_dates:
        return None
    
    date_set = set(available_dates)
    date_objects = [datetime.strptime(d, "%Y-%m-%d").date() for d in available_dates]
    
    # 确定显示的月份
    if current_date:
        try:
            display_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        except:
            display_date = max(date_objects)
    else:
        display_date = max(date_objects)
    
    if f"{key_prefix}_display_year" in st.session_state:
        display_year = st.session_state[f"{key_prefix}_display_year"]
        display_month = st.session_state[f"{key_prefix}_display_month"]
    else:
        display_year = display_date.year
        display_month = display_date.month
    
    selected_new_date = None
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(display_year, display_month)
    
    # 当前选中日期显示
    display_current = current_date.replace("-", "/") if current_date else ""
    months_cn = ["一月", "二月", "三月", "四月", "五月", "六月", 
                 "七月", "八月", "九月", "十月", "十一月", "十二月"]
    
    # 顶部：当前日期输入框样式
    st.markdown(f'''
    <div style="background: rgba(30,41,59,0.8); border: 1px solid rgba(148,163,184,0.3); 
         border-radius: 8px; padding: 8px 12px; margin-bottom: 8px; font-size: 0.95rem; color: #e2e8f0;">
        {display_current}
    </div>
    ''', unsafe_allow_html=True)
    
    # 月份导航
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([0.8, 1.5, 1.5, 0.8, 0.1])
    
    with nav_col1:
        if st.button("‹", key=f"{key_prefix}_prev", help="上月"):
            prev_month = display_month - 1
            prev_year = display_year
            if prev_month < 1:
                prev_month = 12
                prev_year -= 1
            st.session_state[f"{key_prefix}_display_year"] = prev_year
            st.session_state[f"{key_prefix}_display_month"] = prev_month
            st.rerun()
    
    with nav_col2:
        st.markdown(f"<div style='text-align:center; color:#e2e8f0; font-weight:500; padding-top:6px;'>{months_cn[display_month-1]}</div>", unsafe_allow_html=True)
    
    with nav_col3:
        st.markdown(f"<div style='text-align:center; color:#e2e8f0; font-weight:500; padding-top:6px;'>{display_year}</div>", unsafe_allow_html=True)
    
    with nav_col4:
        if st.button("›", key=f"{key_prefix}_next", help="下月"):
            next_month = display_month + 1
            next_year = display_year
            if next_month > 12:
                next_month = 1
                next_year += 1
            st.session_state[f"{key_prefix}_display_year"] = next_year
            st.session_state[f"{key_prefix}_display_month"] = next_month
            st.rerun()
    
    # 星期标题
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    week_cols = st.columns(7)
    for i, wd in enumerate(weekdays):
        with week_cols[i]:
            st.markdown(f"<div style='text-align:center; color:#64748b; font-size:0.8rem; font-weight:500;'>{wd}</div>", unsafe_allow_html=True)
    
    # 日历网格 - 每行7列
    for week in month_days:
        day_cols = st.columns(7)
        for i, day in enumerate(week):
            with day_cols[i]:
                if day == 0:
                    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
                else:
                    date_str = f"{display_year}-{display_month:02d}-{day:02d}"
                    has_data = date_str in date_set
                    is_selected = date_str == current_date
                    
                    if has_data:
                        btn_type = "primary" if is_selected else "secondary"
                        if st.button(str(day), key=f"{key_prefix}_d_{date_str}", type=btn_type, use_container_width=True):
                            selected_new_date = date_str
                    else:
                        # 无数据 - 灰色不可点击
                        st.markdown(f'''
                        <div style="text-align:center; padding:6px 0; color:#334155; font-size:0.85rem;">
                            {day}
                        </div>
                        ''', unsafe_allow_html=True)
    
    return selected_new_date


# ==================== 主页欢迎界面 ====================

def show_homepage():
    """显示欢迎主页（新版布局）"""

    components.html("""
<script>
(function() {
    const parentDoc = window.parent.document;
    const appContainer = parentDoc.querySelector('.stApp');
    if (appContainer && !appContainer.classList.contains('homepage-mode')) {
        appContainer.classList.add('homepage-mode');
    }
})();
</script>
""", height=0)

    # ===== Header 区域 =====
    st.markdown("""
<header class="system-header">
    <div class="logo-group">
        <div class="title-stack">
            <h1><span class="title-icon">🎮</span> 玩家社群<span>分析系统 V2</span></h1>
            <div class="status-badges">
                <span class="badge live">● AI 驱动</span>
                <span class="badge">实时同步</span>
                <span class="badge">新版数据格式</span>
            </div>
        </div>
    </div>
</header>
""", unsafe_allow_html=True)

    # ✅ 查询卡片
    _, center_col, _ = st.columns([1, 3, 1])
    
    with center_col:
        st.markdown('<div class="query-card-header"><span class="header-icon">🔍</span> <span class="header-text">数据查询</span></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🗂️每日查询", "🗃版本查询"])
        
        # === 日常查询标签 ===
        with tab1:
            col_group, col_date = st.columns([1, 1])
            
            with col_group:
                group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
                selected_group_daily = st.selectbox(
                    "🌐 监控社群",
                    options=list(group_options.keys()),
                    format_func=lambda x: group_options[x],
                    key="homepage_group_daily",
                )
                
                # 加载可用日期
                with st.spinner("加载可用日期..."):
                    index = load_index(selected_group_daily)
                    available_dates = index.get("available_dates", [])
            
            with col_date:
                if available_dates:
                    # 转换为date对象列表
                    date_objects = [datetime.strptime(d, "%Y-%m-%d").date() for d in available_dates]
                    max_date = max(date_objects)
                    min_date = min(date_objects)
                    
                    selected_date_obj = st.date_input(
                        "📅 监测日期",
                        value=max_date,
                        min_value=min_date,
                        max_value=max_date,
                        key="homepage_date_daily",
                    )
                    selected_date = selected_date_obj.strftime("%Y-%m-%d") if selected_date_obj else None
                else:
                    st.warning("该社群暂无数据")
                    selected_date = None
            
            # 查询按钮
            st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
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
                st.session_state.confirmed_group = selected_group_daily
                st.session_state.selected_group_cache = selected_group_daily
                st.session_state.confirmed_date = selected_date
                st.session_state.selected_date_cache = selected_date
                st.rerun()


        # === 版本查询标签 ===
        with tab2:
            col_group_v, col_version_v, col_button_v = st.columns([1, 1, 0.8])

            with col_group_v:
                group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
                selected_group_version = st.selectbox(
                    "🌐 监控社群",
                    options=list(group_options.keys()),
                    format_func=lambda x: group_options[x],
                    key="homepage_group_version",
                )

            with col_version_v:
                version_options = {
                    "beta15": "beta15_旋转木马测试（2025-12-03~2025-12-17）",
                    "beta17": "beta17_暖冬测试（2025-12-31~2026-01-20）",
                }
                selected_version_key = st.selectbox(
                    "📦 版本周期",
                    options=list(version_options.keys()),
                    format_func=lambda x: version_options[x],
                    key="homepage_version",
                )

            with col_button_v:
                st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
                if st.button(
                    "✨ 查看分析",
                    use_container_width=True,
                    type="primary",
                    key="btn_version",
                ):
                    st.session_state.show_results = True
                    st.session_state.query_type = "version"
                    st.session_state.selected_group_homepage = selected_group_version
                    st.session_state.selected_version_homepage = selected_version_key
                    st.rerun()

            st.markdown("""
<div style="padding: 0.6rem 1rem; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); 
     border-radius: 10px; margin-top: 0.5rem;">
    <p style="margin: 0; font-size: 0.85rem; color: var(--text-dim);">
        💡 版本查询将展示特定版本期间的社群反馈汇总
    </p>
</div>
""", unsafe_allow_html=True)

    # ===== 系统说明文字 =====
    st.markdown("""
<div style="text-align: center; margin: 8px auto 8px; padding: 0 20px;">
    <p style="font-size: 1.3rem; color: var(--text); line-height: 1.5; font-weight: 500; white-space: nowrap; margin: 0;">
        本系统分析玩家社群中的每日与游戏相关聊天内容，提供日常/版本周期内社群发言监控，给运营团队速掌握大盘情况
    </p>
</div>
""", unsafe_allow_html=True)

    # ===== Intro Cards =====
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
        <span class="icon">📋</span>
        <h3>原文追溯</h3>
        <p>支持查看原文发言详情，还原完整讨论场景</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== 主应用 ====================

def main():
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "query_type" not in st.session_state:
        st.session_state.query_type = "daily"
    
    sidebar_state = "expanded" if st.session_state.show_results else "collapsed"
    
    st.set_page_config(
        page_title="玩家社群分析 V2",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state=sidebar_state,
    )

    st.markdown(STYLE_CSS, unsafe_allow_html=True)
    
    if not st.session_state.show_results:
        show_homepage()
        return
    
    components.html("""
<script>
(function() {
    const parentDoc = window.parent.document;
    const appContainer = parentDoc.querySelector('.stApp');
    if (appContainer && appContainer.classList.contains('homepage-mode')) {
        appContainer.classList.remove('homepage-mode');
    }
})();
</script>
""", height=0)
    
    # 侧边栏
    with st.sidebar:
        st.header("🔍 查询条件")

        group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
        
        default_group_index = 0
        if "selected_group_homepage" in st.session_state:
            try:
                default_group_index = list(group_options.keys()).index(st.session_state.selected_group_homepage)
            except:
                pass
        
        if "confirmed_group" not in st.session_state:
            default_group_key = list(group_options.keys())[default_group_index]
            st.session_state.confirmed_group = default_group_key
        
        if "selected_group_cache" not in st.session_state:
            st.session_state.selected_group_cache = st.session_state.confirmed_group
        
        selected_group_key = st.selectbox(
            "选择社群",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            index=default_group_index,
        )
        
        st.session_state.selected_group_cache = selected_group_key
        display_group_key = selected_group_key

        st.markdown("---")

        current_query_type = st.session_state.get("query_type", "daily")

        with st.spinner("加载数据列表..."):
            index = load_index(display_group_key)
            
            if current_query_type == "version":
                available_versions = index.get("available_versions", [])
            else:
                available_dates = index.get("available_dates", [])

        if current_query_type == "version":
            if available_versions:
                st.success(f"✅ 共有 {len(available_versions)} 个版本")
                
                version_display_map = {}
                for v_key in available_versions:
                    v_info = load_version_info(display_group_key, v_key)
                    version_name = v_info.get("version", v_key)
                    period = v_info.get("period", "")
                    if period:
                        period_formatted = period.replace(" ", "").replace("~", "~")
                        version_display_map[v_key] = f"{version_name}（{period_formatted}）"
                    else:
                        version_display_map[v_key] = version_name
                
                if "confirmed_version" not in st.session_state:
                    if "selected_version_homepage" in st.session_state:
                        st.session_state.confirmed_version = st.session_state.selected_version_homepage
                    else:
                        st.session_state.confirmed_version = available_versions[0] if available_versions else ""
                
                default_version_index = 0
                if st.session_state.get("confirmed_version") in available_versions:
                    try:
                        default_version_index = available_versions.index(st.session_state.confirmed_version)
                    except:
                        pass
                elif "selected_version_homepage" in st.session_state:
                    try:
                        default_version_index = available_versions.index(st.session_state.selected_version_homepage)
                    except:
                        pass
                
                selected_version = st.selectbox(
                    "选择版本",
                    options=available_versions,
                    format_func=lambda x: version_display_map.get(x, x),
                    index=default_version_index,
                    help="选择要查看的测试版本"
                )
                
                st.session_state.selected_version_cache = selected_version
            else:
                st.warning("⚠️ 该社群暂无版本数据")
                selected_version = None
        
        elif available_dates:
            st.success(f"✅ 共有 {len(available_dates)} 天的数据")

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
                if "confirmed_date" not in st.session_state:
                    st.session_state.confirmed_date = default_date.strftime("%Y-%m-%d")

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
                        help="只能选择已上传到数据库的日期",
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
                        help="只能选择已上传到数据库的日期",
                        key="selected_date_input",
                        on_change=on_date_change
                    )

                picker_date = selected_date_obj.strftime("%Y-%m-%d")
                if picker_date in available_dates:
                    st.session_state.selected_date_cache = picker_date
                
                confirmed_group = st.session_state.get("confirmed_group", "")
                confirmed_date = st.session_state.get("confirmed_date", "")
                
                if confirmed_group and confirmed_group != display_group_key:
                    confirmed_group_index = load_index(confirmed_group)
                    confirmed_available_dates = confirmed_group_index.get("available_dates", [])
                else:
                    confirmed_available_dates = available_dates
                
                if not confirmed_date:
                    st.session_state.confirmed_date = default_date.strftime("%Y-%m-%d")
                    confirmed_date = st.session_state.confirmed_date
                
                if not confirmed_group:
                    st.session_state.confirmed_group = display_group_key
                    confirmed_group = display_group_key
                    confirmed_available_dates = available_dates
                
                if confirmed_date in confirmed_available_dates:
                    selected_date = confirmed_date
                else:
                    if confirmed_available_dates:
                        st.session_state.confirmed_date = confirmed_available_dates[0]
                        selected_date = st.session_state.confirmed_date
                    else:
                        selected_date = None
            else:
                selected_date = None
        else:
            st.warning("⚠️ 暂无数据")
            selected_date = None

        st.markdown("---")
        st.caption("💡 数据每日自动更新到 GitHub")
        
        current_confirmed = st.session_state.get("confirmed_date", "")
        current_selected = st.session_state.get("selected_date_cache", "")
        
        current_confirmed_group = st.session_state.get("confirmed_group", "")
        current_selected_group = st.session_state.get("selected_group_cache", "")
        group_changed = current_selected_group and current_confirmed_group and current_selected_group != current_confirmed_group
        
        date_changed = current_selected and current_confirmed and current_selected != current_confirmed
        
        if group_changed or date_changed:
            hint_parts = []
            if group_changed:
                new_group_name = GROUPS.get(current_selected_group, {}).get("name", current_selected_group)
                hint_parts.append(f"社群「{new_group_name}」")
            if date_changed:
                try:
                    selected_formatted = datetime.strptime(current_selected, "%Y-%m-%d").strftime("%m月%d日")
                    hint_parts.append(f"{selected_formatted}")
                except:
                    pass
            if hint_parts:
                st.info(f"📅 已选择 {'、'.join(hint_parts)}，点击下方按钮加载数据")

        if st.button("🔄 刷新数据", use_container_width=True):
            st.session_state.confirmed_group = st.session_state.get("selected_group_cache", "")
            
            if current_query_type == "version":
                st.session_state.confirmed_version = st.session_state.get("selected_version_cache", "")
            else:
                st.session_state.confirmed_date = st.session_state.get("selected_date_cache", "")
            
            st.cache_data.clear()
            _set_nonce()
            st.rerun()
        
        if st.button("🏠 返回主页", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.query_type = "daily"
            st.rerun()

    # 主内容区
    query_type = st.session_state.get("query_type", "daily")
    
    if query_type == "version":
        confirmed_version = st.session_state.get("confirmed_version", "")
        confirmed_group_version = st.session_state.get("confirmed_group", "")
        
        if not confirmed_version:
            confirmed_version = st.session_state.get("selected_version_homepage", "")
            confirmed_group_version = st.session_state.get("selected_group_homepage", "")
        
        if confirmed_version and confirmed_group_version:
            with st.spinner(f"正在加载版本数据..."):
                version_result = load_version_result(confirmed_group_version, confirmed_version)
            
            if version_result:
                render_version_result(version_result, confirmed_group_version)
            else:
                st.error(f"❌ 版本 {confirmed_version} 的数据待上传")
        else:
            st.info("👈 请在侧边栏选择社群和版本")
    else:
        confirmed_group_for_load = st.session_state.get("confirmed_group", selected_group_key)
        confirmed_date = st.session_state.get("confirmed_date", "")
        
        if confirmed_date:
            with st.spinner(f"正在加载 {confirmed_date} 的数据..."):
                result = load_result(confirmed_group_for_load, confirmed_date)
                # 获取可用日期列表用于日期导航
                nav_index = load_index(confirmed_group_for_load)
                nav_available_dates = nav_index.get("available_dates", [])

            if result:
                render_result(result, confirmed_group_for_load, nav_available_dates)
            else:
                st.error(f"❌  {confirmed_date} 的数据待上传")
        else:
            st.info("👈 请在侧边栏选择社群和日期")

if __name__ == "__main__":
    main()
