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
from datetime import datetime, timedelta
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

# 版本周期配置（新增版本在列表末尾追加即可，颜色会自动交替）
VERSION_PERIODS = [
    {"name": "beta17_暖冬测试",   "start": "2025-12-31", "end": "2026-01-20"},
    {"name": "beta18_地图炮测试",  "start": "2026-01-21", "end": "2026-02-03"},
    {"name": "beta19_立春测试",    "start": "2026-02-04", "end": "2026-02-24"},
    {"name": "beta23_新药测试",    "start": "2026-04-29", "end": "2026-05-19"},
    {"name": "beta24_新药测试",    "start": "2026-05-20", "end": "2026-06-02"},
]
# 交替使用的两种颜色（背景色, 文字色）
VERSION_COLOR_A = ("#C8A2E8", "#4c1d95")  # 紫色系
VERSION_COLOR_B = ("#A9B9F0", "#1e3a8a")  # 蓝色系

# ==================== CSS（收敛版：稳 + 清晰）===================

STYLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
  --primary:#C8A2E8;
  --secondary:#A9B9F0;
  --accent:#9AC9F5;
  --accent-primary:#C8A2E8;
  --accent-secondary:#9AD9E8;

  --bg-dark:#f8f9fa;
  --bg0:#ffffff;
  --bg1:#f8f9fa;
  --bg2:#f1f3f5;

  --card:#ffffff;
  --card2:#f8f9fa;
  --card-bg:rgba(255, 255, 255, 0.95);
  --line:rgba(0,0,0,.08);
  --glass-border:rgba(200, 162, 232, 0.25);

  --text:#1a1a2e;
  --muted:#6c757d;
  --muted2:#adb5bd;
  --text-dim:#6c757d;
}

/* ===== App 背景 + 基础字体色 ===== */
.stApp{
  background: radial-gradient(1200px 800px at 20% 0%, rgba(200,162,232,.15), transparent 60%),
              radial-gradient(1000px 700px at 85% 30%, rgba(154,201,245,.12), transparent 55%),
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

/* 减少顶部空白 */
.block-container{
  padding-top: 1rem !important;
}
div[data-testid="stAppViewBlockContainer"]{
  padding-top: 1rem !important;
}

/* 隐藏顶部 header */
header[data-testid="stHeader"]{
  display: none !important;
}
.stApp > header{
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
  background: linear-gradient(90deg, #C8A2E8, #A9B9F0, #9AC9F5);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  text-align:center;
  margin-bottom: .35rem;
  text-shadow: 0 0 26px rgba(200, 162, 232, 0.28);
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
  background: linear-gradient(180deg, #ffffff, #f8f9fa) !important;
  border-right: 1px solid rgba(200,162,232,.2);
  min-width: 280px !important;
  max-width: 320px !important;
}
/* 禁用侧边栏收缩按钮 */
button[data-testid="collapsedControl"],
button[data-testid="stSidebarNavCollapseIcon"],
div[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
div[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] > div > div > div > button:first-child {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
}
/* 确保侧边栏始终展开 */
section[data-testid="stSidebar"][aria-expanded="false"] {
  display: block !important;
  transform: none !important;
  width: 280px !important;
}
section[data-testid="stSidebar"] > div {
  width: 100% !important;
  padding: 1rem 1.2rem !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{ color: #6b21a8 !important; }
section[data-testid="stSidebar"] h5{ 
    color: #7c3aed !important; 
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    margin: 1rem 0 0.5rem 0 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] span{ color: var(--text); }
section[data-testid="stSidebar"] .stCaption{ color: var(--muted) !important; }

/* sidebar 按钮样式 */
section[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #C8A2E8 0%, #A9B9F0 100%) !important;
    border: none !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 0.85rem !important;
    margin: 0.3rem 0 !important;
    color: #1e1b4b !important;
}
section[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #b794d4 0%, #98a8e0 100%) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(200, 162, 232, 0.4) !important;
}
section[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(200, 162, 232, 0.4) !important;
    color: #334155 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    margin: 0.3rem 0 !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(200, 162, 232, 0.15) !important;
    border-color: rgba(200, 162, 232, 0.6) !important;
}

/* 返回主页按钮 */
section[data-testid="stSidebar"] button#st-key-sidebar_back_home {
    background: linear-gradient(135deg, rgba(200,162,232,0.15), rgba(169,185,240,0.15)) !important;
    border: 1px solid rgba(200, 162, 232, 0.4) !important;
    color: #6b21a8 !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] button#st-key-sidebar_back_home:hover {
    background: linear-gradient(135deg, rgba(200,162,232,0.25), rgba(169,185,240,0.25)) !important;
    border-color: rgba(200, 162, 232, 0.6) !important;
    transform: translateX(-2px) !important;
    box-shadow: 0 4px 12px rgba(200, 162, 232, 0.3) !important;
}
section[data-testid="stSidebar"] button#st-key-sidebar_back_home p,
section[data-testid="stSidebar"] button#st-key-sidebar_back_home span {
    color: #6b21a8 !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}

/* 前一天/后一天快捷按钮 */
section[data-testid="stSidebar"] button#st-key-quick_prev_day,
section[data-testid="stSidebar"] button#st-key-quick_next_day,
section[data-testid="stSidebar"] button#st-key-quick_prev_disabled,
section[data-testid="stSidebar"] button#st-key-quick_next_disabled {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(200, 162, 232, 0.35) !important;
    color: #6b21a8 !important;
    font-size: 0.42rem !important;
    padding: 0.2rem 0.25rem !important;
    min-height: auto !important;
    height: auto !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    line-height: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
section[data-testid="stSidebar"] button#st-key-quick_prev_day p,
section[data-testid="stSidebar"] button#st-key-quick_next_day p,
section[data-testid="stSidebar"] button#st-key-quick_prev_disabled p,
section[data-testid="stSidebar"] button#st-key-quick_next_disabled p {
    font-size: 0.42rem !important;
    margin: 0 !important;
    white-space: nowrap !important;
    line-height: 1 !important;
}
section[data-testid="stSidebar"] button#st-key-quick_prev_day span,
section[data-testid="stSidebar"] button#st-key-quick_next_day span,
section[data-testid="stSidebar"] button#st-key-quick_prev_disabled span,
section[data-testid="stSidebar"] button#st-key-quick_next_disabled span {
    font-size: 0.42rem !important;
    white-space: nowrap !important;
    line-height: 1 !important;
}
section[data-testid="stSidebar"] button#st-key-quick_prev_day:hover,
section[data-testid="stSidebar"] button#st-key-quick_next_day:hover {
    background: rgba(200, 162, 232, 0.2) !important;
    border-color: rgba(200, 162, 232, 0.5) !important;
    color: #6b21a8 !important;
}
section[data-testid="stSidebar"] button#st-key-quick_prev_disabled,
section[data-testid="stSidebar"] button#st-key-quick_next_disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* sidebar 输入框/下拉框 */
section[data-testid="stSidebar"] [data-baseweb="select"] > div{
  background: rgba(255,255,255,.98) !important;
  border: 1px solid rgba(200,162,232,.3) !important;
  border-radius: 10px !important;
  font-size: 0.9rem !important;
  padding: 0.7rem 0.9rem !important;
  min-height: 3rem !important;
  height: auto !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"]:hover > div{
  border-color: rgba(200, 162, 232, 0.5) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] span{
  white-space: normal !important;
  word-wrap: break-word !important;
  overflow: visible !important;
  text-overflow: clip !important;
  line-height: 1.5 !important;
  display: inline-block !important;
  max-width: 100% !important;
  vertical-align: middle !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="popover"] {
  max-width: none !important;
}
/* 确保选择器的值区域能完整显示 */
section[data-testid="stSidebar"] [data-baseweb="select"] > div > div {
  overflow: visible !important;
  white-space: normal !important;
  height: auto !important;
  min-height: 1.5rem !important;
}
/* 选择器内部的文本容器 */
section[data-testid="stSidebar"] [data-baseweb="select"] [role="button"] {
  height: auto !important;
  min-height: 1.8rem !important;
  padding-right: 2rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"]{
  background: rgba(255,255,255,.98) !important;
  border: 1px solid rgba(200,162,232,.3) !important;
  border-radius: 10px !important;
  font-size: 0.95rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"]:hover{
  border-color: rgba(200, 162, 232, 0.5) !important;
}
section[data-testid="stSidebar"] input{
  color: var(--text) !important;
}

/* sidebar 分隔线 */
section[data-testid="stSidebar"] hr {
  border: none !important;
  height: 1px !important;
  background: rgba(200, 162, 232, 0.25) !important;
  margin: 1.2rem 0 !important;
}

/* sidebar 提示框 */
section[data-testid="stSidebar"] .stAlert {
  background: rgba(154, 201, 245, 0.15) !important;
  border: 1px solid rgba(154, 201, 245, 0.4) !important;
  border-radius: 8px !important;
  padding: 0.6rem 0.8rem !important;
  font-size: 0.9rem !important;
  margin: 0.5rem 0 !important;
}


/* 全局下拉框和输入框样式 */
[data-baseweb="select"] > div{
  background: rgba(255,255,255,.98) !important;
  border: 1px solid rgba(200,162,232,.3) !important;
  border-radius: 10px !important;
}
[data-baseweb="select"]:hover > div{
  border-color: rgba(200, 162, 232, 0.5) !important;
}
[data-baseweb="input"]{
  background: rgba(255,255,255,.98) !important;
  border: 1px solid rgba(200,162,232,.3) !important;
  border-radius: 10px !important;
}
[data-baseweb="input"]:hover{
  border-color: rgba(200, 162, 232, 0.5) !important;
}
input{
  color: var(--text) !important;
  background: transparent !important;
}

/* 下拉菜单弹层（options） */
div[data-baseweb="menu"]{
  background: rgba(255,255,255,.98) !important;
  border: 1px solid rgba(200,162,232,.25) !important;
  border-radius: 12px !important;
  max-width: 350px !important;
  min-width: 280px !important;
  box-shadow: 0 4px 20px rgba(200,162,232,.2) !important;
}
div[data-baseweb="option"]{ 
  color: var(--text) !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  padding: 0.7rem 1rem !important;
  line-height: 1.4 !important;
}
div[data-baseweb="option"]:hover{ background: rgba(200,162,232,.15) !important; }

/* 日期 popover - 亮色主题 */
div[data-baseweb="popover"]{
  background: #ffffff !important;
  border: 1px solid rgba(200,162,232,.3) !important;
  border-radius: 12px !important;
  z-index: 9999 !important;
  box-shadow: 0 4px 20px rgba(200,162,232,.15) !important;
}
/* 确保所有日期格子可点击（不阻挡原生事件） */
div[data-baseweb="popover"] div[role="gridcell"]{
  cursor: pointer;
}
/* 选中日期 */
div[data-baseweb="popover"] div[role="gridcell"][aria-selected="true"]{
  background: #B592E8 !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
}

/* 确保 components.html 的 iframe 不阻挡日历弹出层 */
iframe[height="0"], iframe[style*="height: 0"]{
  pointer-events: none !important;
  position: absolute !important;
  z-index: -1 !important;
}

/* ===== 按钮 ===== */
.stButton > button{
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  color: #1e1b4b !important;
  border: none;
  border-radius: 12px;
  padding: 0.72rem 1.2rem;
  font-weight: 800;
  transition: all .22s ease;
  box-shadow: 0 8px 22px rgba(200,162,232,.30);
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(200,162,232,.40);
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

/* ===== 下载按钮 ===== */
.stDownloadButton > button,
button[data-testid="baseButton-secondary"]{
  background: linear-gradient(90deg, rgba(200,162,232,.15), rgba(169,185,240,.15)) !important;
  color: #6b21a8 !important;
  border: 1px solid rgba(200,162,232,.4) !important;
  border-radius: 12px !important;
  padding: 0.72rem 1.2rem !important;
  font-weight: 700 !important;
  transition: all .22s ease !important;
  box-shadow: 0 4px 12px rgba(200,162,232,.15) !important;
}
.stDownloadButton > button:hover,
button[data-testid="baseButton-secondary"]:hover{
  background: linear-gradient(90deg, rgba(200,162,232,.25), rgba(169,185,240,.25)) !important;
  border-color: rgba(200,162,232,.6) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 20px rgba(200,162,232,.25) !important;
}
.stDownloadButton > button span,
.stDownloadButton > button p{
  color: #6b21a8 !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
}

/* ===== 统计概览卡 ===== */
.stats-overview{
  background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(248,249,250,.98));
  border-radius: 18px;
  padding: 0.8rem 1rem 0.8rem 1rem;
  margin: 1.1rem 0 1.1rem 0;
  border: 1px solid rgba(200,162,232,.2);
  box-shadow: 0 12px 30px rgba(200,162,232,.15);
}
.stats-overview h2{
  color: #6b21a8;
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
  background: rgba(200,162,232,.1);
  border: 1px solid rgba(200,162,232,.2);
  border-radius: 14px;
  padding: .95rem .9rem;
  text-align:center;
}
.stat-value{
  font-size: 1.85rem;
  font-weight: 900;
  color: #6b21a8;
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
  background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(248,249,250,.98));
  border: 1px solid rgba(200,162,232,.2);
  border-radius: 14px;
  padding: 10px 14px 8px 14px;
  box-shadow: 0 8px 20px rgba(200,162,232,.12);
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
  background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(248,249,250,.98)) !important;
  backdrop-filter: blur(10px) !important;
  border-bottom: 1px solid rgba(200,162,232,.2) !important;
  box-shadow: 0 4px 12px rgba(200,162,232,.1) !important;
}
.cluster-header-inner .cluster-title{
  font-weight: 950 !important;
  font-size: 1.3rem !important;
  color: #334155 !important;
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
  color: #334155;
  line-height: 1.25;
}
.cluster-meta{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.meta-chip{
  background: rgba(200,162,232,.12);
  border: 1px solid rgba(200,162,232,.25);
  border-radius: 999px;
  padding: 6px 10px;
  font-size: .86rem;
  color: var(--text);
}
.meta-chip span{
  color: #6b21a8;
  font-weight: 700;
  margin-right: 6px;
}
.badge-heat{
  flex: 0 0 auto;
  padding: 7px 10px;
  border-radius: 999px;
  font-weight: 950;
  color:#334155;
  background: linear-gradient(90deg, rgba(200,162,232,.95), rgba(169,185,240,.95));
  box-shadow: 0 8px 20px rgba(200,162,232,.25);
  white-space: nowrap;
}
.badge-heat small{
  opacity:.88;
  font-weight: 800;
  margin-right: 4px;
}

.heatbar-wrap{
  margin-top: 6px;
  background: rgba(200,162,232,.12);
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  border: 1px solid rgba(200,162,232,.15);
}
.heatbar{
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #C8A2E8, #A9B9F0, #9AC9F5);
  box-shadow: 0 2px 8px rgba(200,162,232,0.35);
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
  background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(248,249,250,.98));
  border: 1px solid rgba(200,162,232,.2);
  border-radius: 14px;
  padding: 10px 14px 8px 14px;
  box-shadow: 0 8px 20px rgba(200,162,232,.12);
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
  background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(255,255,255,0.98) 85%, rgba(255,255,255,0.7) 100%) !important;
  padding-bottom: 6px;
  margin-bottom: 0;
}
.cluster-card-sticky .cluster-card{
  background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(248,249,250,.98));
  border: 1px solid rgba(200,162,232,.2);
  border-radius: 14px;
  padding: 10px 14px 8px 14px;
  box-shadow: 0 8px 20px rgba(200,162,232,.12);
}
/* 可滚动内容区域 */
.scrollable-content{
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(248,250,252,.5);
  border: 1px solid rgba(200,162,232,.15);
  border-radius: 14px;
  scrollbar-width: thin;
  scrollbar-color: rgba(200,162,232,.35) transparent;
  padding-bottom: 400px; /* 底部留白，让最后的讨论点也能滚动到顶部 */
}
.scrollable-content::-webkit-scrollbar{
  width: 8px;
}
.scrollable-content::-webkit-scrollbar-track{
  background: transparent;
}
.scrollable-content::-webkit-scrollbar-thumb{
  background: rgba(200,162,232,.35);
  border-radius: 4px;
}
/* 内部收起按钮 */
.expander-toggle-inside{
  background: rgba(255,255,255,.95);
  border: 1px solid rgba(200,162,232,.25);
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
  background: rgba(200,162,232,.15);
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
  background: linear-gradient(145deg, rgba(200,162,232,.15), rgba(169,185,240,.1));
  border: 1px solid rgba(200,162,232,.3);
  border-radius: 10px;
  padding: 8px 16px;
  margin: 12px 10px 6px 10px;
  text-align: center;
  color: #6b21a8;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.expander-toggle-bottom:hover{
  background: linear-gradient(145deg, rgba(200,162,232,.25), rgba(169,185,240,.2));
  border-color: rgba(200,162,232,.45);
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
  background: rgba(255,255,255,.95);
  border: 1px solid rgba(200,162,232,.25);
  border-radius: 14px;
  padding: 6px 14px;
  text-align: left;
  color: var(--text);
  font-weight: 900;
  transition: all 0.2s ease;
}
.expander-toggle:hover{
  background: rgba(200,162,232,.15);
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
  background: rgba(255,255,255,.95) !important;
  border: 1px solid rgba(200,162,232,.25) !important;
  border-radius: 14px !important;
  padding: 10px 14px !important;
}
section[data-testid="stMain"] div[data-testid="stExpander"] details > summary *{
  color: var(--text) !important;
  font-weight: 900 !important;
}
section[data-testid="stMain"] div[data-testid="stExpander"] div[role="region"]{
  background: rgba(248,250,252,.6) !important;
  border: 1px solid rgba(200,162,232,.15) !important;
  border-radius: 14px !important;
  padding: 12px 14px !important;
}

/* ===== 讨论点 / 观点 / 引用 ===== */
.discussion-point{
  background: #f8f9fa;
  border-left: 3px solid #C8A2E8;
  padding: .7rem 1rem;
  margin: .6rem 0;
  border-radius: 0 8px 8px 0;
}
.discussion-point strong{ color:#1a1a2e; font-size: 1rem; }

/* 讨论点可展开卡片 */
.dp-expander{
  margin: 6px 0;
  border-radius: 8px;
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
  background: linear-gradient(135deg, rgba(133,182,242,0.1) 0%, rgba(117,200,227,0.1) 100%);
  border: 1px solid rgba(133,182,242,0.3);
  border-left: 4px solid #85B6F2;
  border-radius: 0 10px 10px 0;
  padding: 12px 16px;
  transition: all 0.2s ease;
}
.dp-card:hover{
  background: linear-gradient(135deg, rgba(133,182,242,0.18) 0%, rgba(117,200,227,0.18) 100%);
  border-color: rgba(133,182,242,0.5);
  border-left-color: #5a9de8;
}
.dp-header{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.dp-title{
  font-weight: 700;
  font-size: 1.05rem;
  color: #2563eb;
  flex: 1;
}
.dp-toggle-btn{
  font-size: 0.72rem;
  font-weight: 500;
  color: #6b7280;
  background: transparent;
  padding: 3px 8px;
  border-radius: 4px;
  border: none;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.dp-card:hover .dp-toggle-btn{
  color: #4b5563;
}
.dp-toggle-btn .expand-text{ display: inline; }
.dp-toggle-btn .collapse-text{ display: none; }
.dp-expander[open] .dp-toggle-btn{
  color: #4b5563;
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
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}
/* 讨论点Sticky卡片 */
.dp-card-sticky{
  position: sticky;
  top: 0;
  z-index: 50;
  background: #ffffff;
  padding-bottom: 4px;
}
.dp-card-sticky .dp-card{
  background: linear-gradient(135deg, rgba(133,182,242,0.1) 0%, rgba(117,200,227,0.1) 100%);
  border: 1px solid rgba(133,182,242,0.3);
  border-left: 4px solid #85B6F2;
  border-radius: 0 10px 10px 0;
  margin: 0;
  cursor: pointer;
  transition: all 0.2s ease;
}
.dp-card-sticky .dp-card:hover{
  background: linear-gradient(135deg, rgba(133,182,242,0.18) 0%, rgba(117,200,227,0.18) 100%);
}
/* 讨论点内容区域（自适应高度，无需滚动） */
.dp-scrollable{
  overflow: visible;
}
/* 讨论点收起按钮 */
.dp-collapse-btn{
  background: transparent;
  border: none;
  padding: 6px 12px;
  margin: 8px 10px;
  text-align: left;
  color: #6c757d;
  font-weight: 500;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.dp-collapse-btn:hover{
  color: #495057;
}
.dp-content{
  background: #ffffff;
  padding: 12px 14px;
}

/* ===== 讨论点直接展示样式（不折叠）===== */
.dp-card-wrapper{
  background: #ffffff;
  border: 1px solid rgba(181,146,232,0.3);
  border-left: 5px solid #B592E8;
  border-radius: 0 12px 12px 0;
  margin: 18px 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(181,146,232,0.08);
}
.dp-card-header-fixed{
  background: linear-gradient(135deg, rgba(181,146,232,0.18) 0%, rgba(133,182,242,0.15) 100%);
  border-bottom: 1px solid rgba(133,182,242,0.3);
  padding: 14px 18px;
}
.dp-card-header-fixed .dp-title{
  font-weight: 800;
  font-size: 1.2rem;
  color: #4c1d95;
  letter-spacing: 0.02em;
}
.dp-content-direct{
  background: rgba(248,249,250,0.5);
  padding: 14px 18px 14px 22px;
  border-left: 2px solid rgba(181,146,232,0.15);
  margin-left: 6px;
}

/* 讨论点主标题（最高层级） */
.dp-main-title{
  background: linear-gradient(135deg, #B592E8 0%, #9AA0F0 100%);
  border-left: none;
  border-radius: 10px;
  padding: 14px 20px;
  margin-bottom: 18px;
  color: #ffffff;
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  box-shadow: 0 3px 12px rgba(181,146,232,0.25);
}
.dp-section-title{
  font-size: 0.84rem;
  font-weight: 600;
  color: #6366f1;
  background: transparent;
  border: none;
  padding: 0;
  margin: 12px 0 6px 0;
  display: flex;
  align-items: center;
  gap: 5px;
}
.dp-section-title:first-child{
  margin-top: 0;
}

.opinion-item{
  background: linear-gradient(135deg, rgba(169,185,240,0.10) 0%, rgba(133,182,242,0.10) 100%);
  border: none;
  border-left: 3px solid #A9B9F0;
  padding: 10px 14px;
  margin: 8px 0;
  border-radius: 0 8px 8px 0;
  color: #1f2937;
  font-size: 0.92rem;
  line-height: 1.6;
  font-weight: 600;
}
.example-quote{
  background: rgba(169,185,240,0.1);
  border: none;
  border-left: 2px solid #A9B9F0;
  padding: 10px 14px;
  margin: 8px 0;
  border-radius: 0 6px 6px 0;
  color: #374151;
  font-style: italic;
  font-size: 0.88rem;
  line-height: 1.5;
}

/* ===== 新增：观点卡片样式（V2格式）===== */
.opinion-card{
  background: linear-gradient(135deg, rgba(169,185,240,0.10) 0%, rgba(133,182,242,0.10) 100%) !important;
  border: 1px solid rgba(169,185,240,0.30) !important;
  border-left: 3px solid #A9B9F0 !important;
  border-radius: 0 8px 8px 0 !important;
  padding: 12px 16px;
  margin: 10px 0;
}
.opinion-card-header{
  font-size: 0.95rem;
  font-weight: 600;
  color: #4f46e5 !important;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.4;
}
.opinion-card-content{
  margin-left: 4px;
}

/* 原文发言展开器 */
.raw-msg-expander{
  margin-top: 10px;
  border-radius: 6px;
}
.raw-msg-summary{
  list-style: none;
  cursor: pointer;
  user-select: none;
  background: rgba(169,185,240,0.1);
  border: 1px solid rgba(169,185,240,0.3);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.82rem;
  font-weight: 500;
  color: #4f46e5;
  transition: all 0.15s ease;
}
.raw-msg-summary:hover{
  background: rgba(169,185,240,0.2);
  color: #4338ca;
}
.raw-msg-summary::-webkit-details-marker{
  display: none;
}
.raw-msg-expander[open] .raw-msg-summary{
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
.raw-msg-content{
  background: rgba(169,185,240,0.06);
  border: 1px solid rgba(169,185,240,0.25);
  border-top: none;
  border-bottom-left-radius: 6px;
  border-bottom-right-radius: 6px;
  padding: 12px 14px;
  max-height: 300px;
  overflow-y: auto;
}
.raw-msg-item{
  background: #ffffff;
  border: 1px solid rgba(169,185,240,0.25);
  border-left: 3px solid #A9B9F0;
  border-radius: 0 6px 6px 0;
  padding: 10px 14px;
  margin: 8px 0;
  font-size: 0.9rem;
  line-height: 1.5;
}
.raw-msg-item .msg-meta{
  color: #4f46e5;
  font-size: 0.8rem;
  margin-bottom: 4px;
}
.raw-msg-item .msg-content{
  color: #1f2937;
}

/* Metric */
[data-testid="stMetricValue"]{ color: #6b21a8 !important; font-weight: 900 !important; }
[data-testid="stMetricLabel"]{ color: var(--muted) !important; }

a{ color:#7c3aed !important; text-decoration: none !important; }
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
  background: linear-gradient(to bottom, rgba(200, 162, 232, 0.1), transparent);
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
  color: #334155;
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
  color: #059669;
  border-color: rgba(174, 228, 222, 0.5);
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
  box-shadow: 0 20px 50px rgba(0,0,0,0.15);
}
.query-modes{
  display: flex;
  gap: 4px;
  background: rgba(200,162,232,0.1);
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
  background: rgba(200,162,232,0.2);
  color: #334155;
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
  background: rgba(200,162,232,0.1);
  border: 1px solid var(--glass-border);
  color: #334155;
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
  background: linear-gradient(to right, #C8A2E8, #A9B9F0);
  color: #1e1b4b;
  border: none;
  padding: 14px 32px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 10px 20px rgba(200, 162, 232, 0.3);
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
.intro-card h3{ margin: 0 0 10px; font-size: 1.25rem; font-weight: 700; color: #334155; }
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
  background: rgba(200,162,232,0.15) !important;
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
  background: rgba(200,162,232,0.2) !important;
  border-color: rgba(200,162,232,0.5) !important;
}
/* Tab按钮选中状态 */
div[data-baseweb="tab-list"] button[aria-selected="true"],
.stTabs [aria-selected="true"],
button[aria-selected="true"]{
  background: linear-gradient(135deg, rgba(200,162,232,0.4), rgba(169,185,240,0.3)) !important;
  color: #1e1b4b !important;
  border-color: #C8A2E8 !important;
  box-shadow: 0 8px 24px rgba(200, 162, 232, 0.4) !important;
  text-shadow: 0 0 12px rgba(200, 162, 232, 0.6) !important;
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
  border-bottom: 1px solid rgba(200, 162, 232, 0.25);
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
  filter: drop-shadow(0 0 8px rgba(200, 162, 232, 0.2));
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
  background: rgba(200, 162, 232, 0.18);
  border-color: rgba(200, 162, 232, 0.35);
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
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 249, 250, 0.98));
  border: 1px solid rgba(200, 162, 232, 0.35);
  border-radius: 12px;
  padding: 12px 16px;
  min-width: 280px;
  max-width: 450px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15), 0 0 20px rgba(200, 162, 232, 0.15);
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
  color: #6b21a8;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.time-tooltip-wrapper .tooltip-content .tooltip-text{
  font-size: 0.88rem;
  color: #334155;
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
  color: #9333ea;
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
  color: #6b21a8 !important;
  margin-bottom: 10px !important;
  letter-spacing: 0.02em !important;
}

/* Streamlit label 内部的 p 标签 */
[data-testid="stWidgetLabel"] p{
  font-size: 1.4rem !important;
  font-weight: 800 !important;
  color: #6b21a8 !important;
}

/* 主页查询区域 - 下拉框宽度缩短 */
section[data-testid="stMain"] [data-testid="stSelectbox"]{
  max-width: 350px !important;
}
section[data-testid="stMain"] [data-testid="stDateInput"]{
  max-width: 350px !important;
}

/* 主页查询区域 - 下拉框文字清晰 */
section[data-testid="stMain"] [data-baseweb="select"] *{
  color: #1f2937 !important;
  opacity: 1 !important;
  -webkit-text-fill-color: #1f2937 !important;
}
section[data-testid="stMain"] [data-baseweb="select"] [role="button"]{
  font-weight: 600 !important;
  font-size: 0.95rem !important;
}
section[data-testid="stMain"] [data-baseweb="select"] > div:first-child{
  background: #ffffff !important;
  border: 1.5px solid #d1d5db !important;
  border-radius: 8px !important;
}
section[data-testid="stMain"] [data-baseweb="select"] > div:first-child:hover{
  border-color: #B592E8 !important;
}
section[data-testid="stMain"] [data-baseweb="select"] svg{
  fill: #6b7280 !important;
  color: #6b7280 !important;
}

/* 查询区域容器样式 - 通过标记ID定位 */
[data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] > .query-card-header){
  background: rgba(255, 255, 255, 0.95) !important;
  border: 2px solid var(--accent-primary) !important;
  border-radius: 20px !important;
  padding: 20px 24px !important;
  margin-bottom: 20px !important;
  box-shadow: 0 15px 40px rgba(200, 162, 232, 0.2) !important;
}
/* ===== Fix: 侧边栏 前一天/后一天 按钮不换行（强制一行显示） ===== */
section[data-testid="stSidebar"] button#st-key-prev_day,
section[data-testid="stSidebar"] button#st-key-next_day,
section[data-testid="stSidebar"] button#st-key-prev_day_disabled,
section[data-testid="stSidebar"] button#st-key-next_day_disabled{
  width: 100% !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;

  /* 关键：禁止在 / 等符号处断行 */
  overflow-wrap: normal !important;
  word-break: keep-all !important;

  font-size: 0.9rem !important;
  line-height: 1 !important;
  padding: 8px 10px !important;
}

/* 按钮内部文字（p/span）也锁死不换行 */
section[data-testid="stSidebar"] button#st-key-prev_day p,
section[data-testid="stSidebar"] button#st-key-next_day p,
section[data-testid="stSidebar"] button#st-key-prev_day_disabled p,
section[data-testid="stSidebar"] button#st-key-next_day_disabled p,
section[data-testid="stSidebar"] button#st-key-prev_day span,
section[data-testid="stSidebar"] button#st-key-next_day span{
  margin: 0 !important;
  padding: 0 !important;
  white-space: nowrap !important;
  overflow-wrap: normal !important;
  word-break: keep-all !important;
  line-height: 1 !important;
}

/* 让两列更不容易互相挤爆（可选但建议加） */
section[data-testid="stSidebar"] [data-testid="column"]{
  min-width: 0 !important;
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
    
    # 报告标题
    st.markdown(
        f"""<div style="text-align: center; padding: 0 0 1rem 0;">
<h1 style="margin: 0; color: #6b21a8; font-size: 2rem; font-weight: 700;">
📊 {platform_display} {group_display} {formatted_date} 分析报告 <span style="color: #C8A2E8;">_热门讨论TOP5</span>
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
            discussion_content_html += f'<div class="dp-main-title">💬 讨论点（共 {len(discussion_list)} 条）</div>'
            
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
<div style="position: absolute; right: 14px; bottom: 10px; font-size: 0.85rem; font-weight: 700; color: #7c3aed;">点击查看详情</div>
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
                    f"""<div style="text-align: center; padding: 0.5rem 1rem; background: rgba(200,162,232,0.25); 
                    border-radius: 8px; border: 2px solid rgba(200,162,232,0.5);">
                    <span style="font-size: 1.45rem; font-weight: 700; color: #6b21a8;">📅 {current_display}</span>
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
<h1 style="margin: 0; color: #6b21a8; font-size: 1.8rem; font-weight: 700; white-space: nowrap;">
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
            discussion_content_html += f'<div class="dp-main-title">📋 核心讨论点（共 {len(discussion_points)} 条）</div>'
            
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
<div style="font-size: 1.5rem; font-weight: 800; color: #6b21a8;">{players}</div>
<div style="font-size: 0.75rem; color: var(--muted);">参与玩家</div>
</div>
<div style="display: flex; flex-direction: column; gap: 4px; align-items: center;">
<div style="font-size: 1.5rem; font-weight: 800; color: #6b21a8;">{msgs}</div>
<div style="font-size: 0.75rem; color: var(--muted);">发言数</div>
</div>
<div class="badge-heat"><small>热度</small>{heat:.2f} 🔥</div>
</div>
</div>

<div style="margin-top: 12px; margin-bottom: 12px;">
<div style="display: inline-block; background: rgba(154,201,245,0.2); color: #0284c7; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; margin-bottom: 0;">热度趋势</div>
<div style="font-size: 0.88rem; color: var(--text); line-height: 1.6;">{heat_trend_escaped}</div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
<div style="font-size: 0.85rem; color: var(--muted);">{date_range} · 持续 {days} 天</div>
<div style="font-size: 0.85rem; font-weight: 700; color: #7c3aed; cursor: pointer;">点击查看详情</div>
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
        
        # JavaScript：动态修改 tab 文字样式
        components.html("""
<script>
(function() {
    const parentDoc = window.parent.document;
    
    function styleTabButtons() {
        // 查找所有tab按钮
        const tabButtons = parentDoc.querySelectorAll('button[data-baseweb="tab"]');
        tabButtons.forEach(btn => {
            btn.style.fontSize = '1.1rem';
            btn.style.fontWeight = '600';
        });
    }
    
    // 初始执行
    styleTabButtons();
    
    // 监听变化
    const observer = new MutationObserver(styleTabButtons);
    observer.observe(parentDoc.body, { childList: true, subtree: true });
})();
</script>
""", height=0)

        # === 日常查询标签 ===
        with tab1:
            col_group, col_date, col_button = st.columns([1, 1, 0.8])

            with col_group:
                # 自定义标签
                st.markdown('<div style="font-size: 1.4rem; font-weight: 800; color: #6b21a8; margin-bottom: 8px;">🌐 监控社群</div>', unsafe_allow_html=True)
                group_options = {k: GROUPS[k]["name"] for k in GROUPS.keys()}
                selected_group_daily = st.selectbox(
                    "",
                    options=list(group_options.keys()),
                    format_func=lambda x: group_options[x],
                    key="homepage_group_daily",
                    label_visibility="collapsed"
                )

                # 加载日期列表
                with st.spinner("加载可用日期..."):
                    index = load_index(selected_group_daily)
                    available_dates = index.get("available_dates", [])

            with col_date:
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

                        # 自定义标签带tooltip
                        st.markdown('<div style="font-size: 1.4rem; font-weight: 800; color: #6b21a8; margin-bottom: 8px;">📅 监测日期</div>', unsafe_allow_html=True)

                        if st.session_state.get("homepage_need_date_correction", False):
                            corrected_date = datetime.strptime(
                                st.session_state.homepage_valid_date_selected, "%Y-%m-%d"
                            ).date()
                            selected_date_obj = st.date_input(
                                "",
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
                                    f'border-left: 3px solid #C8A2E8; border-radius: 8px; margin: 0.5rem 0;">'
                                    f'<p style="margin: 0; font-size: 0.85rem; font-weight: 600; color: #6b21a8;">'
                                    f'⚠️ {formatted_invalid_date}暂无数据，已选择：{formatted_valid_date}</p></div>',
                                    unsafe_allow_html=True,
                                )
                            st.session_state.homepage_need_date_correction = False
                        else:
                            selected_date_obj = st.date_input(
                                "",
                                value=initial_date,
                                min_value=extended_min_date,
                                max_value=extended_max_date,
                                help="选择需要查看的日期",
                                key="homepage_date_input",
                                on_change=on_homepage_date_change,
                                label_visibility="collapsed"
                            )

                        # ===== 版本颜色 CSS 规则（纯CSS，不用JS修改inline style）=====
                        cal_css_parts = []
                        # 默认：所有带 data-date 属性的 gridcell 半透明（不可用）
                        cal_css_parts.append(
                            'div[data-baseweb="popover"] div[role="gridcell"][data-date]{'
                            'opacity:0.35;cursor:default;}'
                        )
                        # 可用日期：正常显示
                        for ad in available_dates:
                            cal_css_parts.append(
                                f'div[data-baseweb="popover"] div[role="gridcell"][data-date="{ad}"]'
                                f'{{opacity:1!important;cursor:pointer!important;}}'
                            )
                        # 版本颜色
                        for vi, vp in enumerate(VERSION_PERIODS):
                            bg_color, text_color = VERSION_COLOR_A if vi % 2 == 0 else VERSION_COLOR_B
                            s = datetime.strptime(vp["start"], "%Y-%m-%d").date()
                            e_date = datetime.strptime(vp["end"], "%Y-%m-%d").date()
                            d = s
                            while d <= e_date:
                                ds = d.strftime("%Y-%m-%d")
                                cal_css_parts.append(
                                    f'div[data-baseweb="popover"] div[role="gridcell"][data-date="{ds}"]'
                                    f'{{background:{bg_color}!important;color:{text_color}!important;'
                                    f'font-weight:700!important;border-radius:6px!important;'
                                    f'opacity:0.9!important;}}'
                                )
                                d += timedelta(days=1)
                        # 溢出日期（相邻月份）
                        cal_css_parts.append(
                            'div[data-baseweb="popover"] div[role="gridcell"][data-overflow]{'
                            'opacity:0.25!important;pointer-events:none!important;}'
                        )
                        st.markdown(f'<style>{" ".join(cal_css_parts)}</style>', unsafe_allow_html=True)

                        # 构建日期→版本名称映射（供JS tooltip用）
                        date_version_map = {}
                        for vp in VERSION_PERIODS:
                            s = datetime.strptime(vp["start"], "%Y-%m-%d").date()
                            e_date = datetime.strptime(vp["end"], "%Y-%m-%d").date()
                            # 格式化显示名：beta17_暖冬测试（12/31~01/20）
                            s_display = s.strftime("%m/%d")
                            e_display = e_date.strftime("%m/%d")
                            label = f'{vp["name"]}（{s_display}~{e_display}）'
                            d = s
                            while d <= e_date:
                                date_version_map[d.strftime("%Y-%m-%d")] = label
                                d += timedelta(days=1)
                        date_version_map_js = json.dumps(date_version_map, ensure_ascii=False)

                        # ===== JavaScript：设置 data 属性 + tooltip + 翻译，绝不修改 inline style =====
                        components.html(f"""
<script>
(function(){{
  var monthMap = {{
    'January':'一月','February':'二月','March':'三月','April':'四月',
    'May':'五月','June':'六月','July':'七月','August':'八月',
    'September':'九月','October':'十月','November':'十一月','December':'十二月'
  }};
  var weekdayMap = {{
    'Mo':'一','Tu':'二','We':'三','Th':'四','Fr':'五','Sa':'六','Su':'日',
    'Mon':'一','Tue':'二','Wed':'三','Thu':'四','Fri':'五','Sat':'六','Sun':'日'
  }};
  var versionMap = {date_version_map_js};

  var parentDoc = window.parent.document;

  function safeReplace(el, map){{
    if(!el.children || !el.children.length){{
      var t = el.textContent || '';
      for(var key in map){{
        if(t.indexOf(key) !== -1 && t.indexOf(map[key]) === -1){{
          el.textContent = t.replace(key, map[key]);
          return;
        }}
      }}
    }} else {{
      for(var i=0; i<el.children.length; i++){{
        safeReplace(el.children[i], map);
      }}
      for(var j=0; j<el.childNodes.length; j++){{
        var node = el.childNodes[j];
        if(node.nodeType === 3){{
          var v = node.nodeValue || '';
          for(var key in map){{
            if(v.indexOf(key) !== -1 && v.indexOf(map[key]) === -1){{
              node.nodeValue = v.replace(key, map[key]);
              return;
            }}
          }}
        }}
      }}
    }}
  }}

  function translateAll(){{
    parentDoc.querySelectorAll('div[data-baseweb="popover"]').forEach(function(pop){{
      pop.querySelectorAll('button').forEach(function(btn){{
        safeReplace(btn, monthMap);
      }});
      pop.querySelectorAll('[role="option"], li').forEach(function(item){{
        safeReplace(item, monthMap);
      }});
      var thead = pop.querySelector('thead');
      if(thead){{
        thead.querySelectorAll('*').forEach(function(el){{
          if(!el.children.length){{
            var t = (el.textContent||'').trim();
            if(weekdayMap[t]) el.textContent = weekdayMap[t];
          }}
        }});
      }}
    }});
  }}

  function labelAllDates(){{
    parentDoc.querySelectorAll('div[data-baseweb="popover"]').forEach(function(pop){{
      var cells = pop.querySelectorAll('div[role="gridcell"]');
      if(!cells.length) return;

      var currentYear = null, currentMonth = null;
      var mEN = ['January','February','March','April','May','June','July','August','September','October','November','December'];
      var mCN = ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'];

      // 兼容各版本 Streamlit：从日历头部区域提取年月
      // 方法1: button[role="combobox"]
      // 方法2: 所有按钮/select
      // 方法3: 日历头部整体文本
      var headerText = '';
      var comboboxes = pop.querySelectorAll('button[role="combobox"]');
      if(comboboxes.length){{
        comboboxes.forEach(function(btn){{
          headerText += ' ' + (btn.textContent || btn.getAttribute('aria-label') || '');
        }});
      }}
      if(!headerText.trim()){{
        // 获取非表格/非gridcell区域的所有文本（即头部导航区域）
        pop.querySelectorAll('button, select, [role="heading"], [data-baseweb="calendar-header"] *').forEach(function(el){{
          if(!el.closest('table') && !el.closest('thead') && !el.closest('[role="grid"]')){{
            headerText += ' ' + (el.textContent || '');
          }}
        }});
      }}
      if(!headerText.trim()){{
        // 最后手段：取 popover 前150字符
        headerText = (pop.textContent || '').substring(0, 150);
      }}

      // 从 headerText 提取年份
      var ym = headerText.match(/(\\d{{4}})/);
      if(ym) currentYear = parseInt(ym[1]);
      // 从 headerText 提取月份（倒序匹配，防止十二月被二月误匹配）
      for(var i=mEN.length-1;i>=0;i--){{
        if(headerText.toLowerCase().indexOf(mEN[i].toLowerCase()) !== -1 || headerText.indexOf(mCN[i]) !== -1){{
          currentMonth = i; break;
        }}
      }}

      if(currentYear===null||currentMonth===null){{
        var now=new Date();
        if(currentYear===null) currentYear=now.getFullYear();
        if(currentMonth===null) currentMonth=now.getMonth();
      }}

      var items = [];
      cells.forEach(function(c){{
        var d = parseInt((c.textContent||'').trim());
        items.push({{cell:c, day:isNaN(d)?-1:d}});
      }});

      var first1=-1;
      for(var i=0;i<items.length;i++){{ if(items[i].day===1){{first1=i;break;}} }}
      var second1=-1;
      if(first1>=0) for(var i=first1+1;i<items.length;i++){{ if(items[i].day===1){{second1=i;break;}} }}

      items.forEach(function(it,idx){{
        var cell=it.cell, day=it.day;
        if(day<1||day>31) return;
        var y=currentYear, m=currentMonth;
        var isOverflow = (first1>=0 && idx<first1) || (second1>=0 && idx>=second1);
        if(first1>=0 && idx<first1){{ m--; if(m<0){{m=11;y--;}} }}
        else if(second1>=0 && idx>=second1){{ m++; if(m>11){{m=0;y++;}} }}
        var ds = y+'-'+String(m+1).padStart(2,'0')+'-'+String(day).padStart(2,'0');
        cell.setAttribute('data-date', ds);
        if(isOverflow) cell.setAttribute('data-overflow','1');
        else cell.removeAttribute('data-overflow');
        // 设置版本 tooltip
        if(versionMap[ds]){{
          cell.setAttribute('title', versionMap[ds]);
        }} else {{
          cell.removeAttribute('title');
        }}
      }});
    }});
  }}

  function runAll(){{
    translateAll();
    labelAllDates();
  }}

  var timer = null;
  var obs = new MutationObserver(function(){{
    clearTimeout(timer);
    timer = setTimeout(runAll, 60);
  }});
  obs.observe(parentDoc.body, {{childList:true, subtree:true, characterData:true}});

  parentDoc.addEventListener('click', function(e){{
    var t = e.target;
    if(t.closest && t.closest('[data-baseweb="popover"]')){{
      setTimeout(runAll, 50);
      setTimeout(runAll, 150);
      setTimeout(runAll, 300);
      setTimeout(runAll, 500);
    }}
  }}, true);

  setTimeout(runAll, 200);
  setTimeout(runAll, 500);
}})();
</script>
""", height=0)

                        selected_date = selected_date_obj.strftime("%Y-%m-%d")
                        if selected_date in available_dates:
                            st.session_state.homepage_date_cache = selected_date
                    else:
                        selected_date = None
                else:
                    st.warning("该社群暂无数据")
                    selected_date = None

            with col_button:
                # 添加顶部间距对齐
                st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
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

    # ===== JavaScript：给查询区域容器添加背景 =====
    components.html("""
<script>
(function() {
    function applyCardBackground() {
        const parentDoc = window.parent.document;
        const header = parentDoc.querySelector('.query-card-header');
        if (header) {
            let container = header.closest('[data-testid="column"]');
            if (!container) container = header.closest('[data-testid="stVerticalBlock"]');
            if (container && !container.dataset.cardStyled) {
                container.dataset.cardStyled = 'true';
                container.style.background = 'rgba(255, 255, 255, 0.95)';
                container.style.border = '2px solid #C8A2E8';
                container.style.borderRadius = '20px';
                container.style.padding = '20px 24px';
                container.style.marginBottom = '20px';
                container.style.boxShadow = '0 15px 40px rgba(200, 162, 232, 0.2)';
            }
        }
    }
    setTimeout(applyCardBackground, 200);
    setTimeout(applyCardBackground, 500);
    setTimeout(applyCardBackground, 1000);
    const observer = new MutationObserver(applyCardBackground);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", height=0)

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
        <h3>热度分析</h3>
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
        # 返回主页按钮
        if st.button("← 返回主页", key="sidebar_back_home", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.query_type = "daily"
            st.rerun()
        
        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <h2 style="margin: 0; font-size: 1.3rem; color: #6b21a8;">🔍 查询条件</h2>
        </div>
        """, unsafe_allow_html=True)

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
        
        st.markdown("##### 🌐 监控社群")
        selected_group_key = st.selectbox(
            "选择社群",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            index=default_group_index,
            label_visibility="collapsed"
        )
        
        st.session_state.selected_group_cache = selected_group_key
        display_group_key = selected_group_key

        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

        current_query_type = st.session_state.get("query_type", "daily")

        with st.spinner("加载数据列表..."):
            index = load_index(display_group_key)
            
            if current_query_type == "version":
                available_versions = index.get("available_versions", [])
            else:
                available_dates = index.get("available_dates", [])

        if current_query_type == "version":
            if available_versions:
                st.markdown("##### 📦 版本周期")
                
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
                    help="选择要查看的测试版本",
                    label_visibility="collapsed"
                )
                
                st.session_state.selected_version_cache = selected_version
            else:
                st.warning("⚠️ 该社群暂无版本数据")
                selected_version = None
        
        elif available_dates:
            st.markdown("##### 📅 监测日期")

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
                        help="选择需要查看的日期",
                        key="selected_date_input",
                        on_change=on_date_change,
                        label_visibility="collapsed"
                    )

                    invalid_date = st.session_state.get("invalid_date_selected", "")
                    valid_date = st.session_state.get("valid_date_selected", "")
                    if invalid_date:
                        formatted_invalid_date = datetime.strptime(invalid_date, "%Y-%m-%d").strftime("%m月%d日")
                        formatted_valid_date = datetime.strptime(valid_date, "%Y-%m-%d").strftime("%m月%d日")
                        st.warning(f"⚠️ {formatted_invalid_date}暂无数据，已自动选择 {formatted_valid_date}")
                    st.session_state.need_date_correction = False
                else:
                    selected_date_obj = st.date_input(
                        "选择日期",
                        value=initial_date,
                        min_value=extended_min_date,
                        max_value=extended_max_date,
                        help="选择需要查看的日期",
                        key="selected_date_input",
                        on_change=on_date_change,
                        label_visibility="collapsed"
                    )

                # ===== 侧边栏日历：版本颜色 CSS + 翻译/tooltip JS =====
                sidebar_cal_css = []
                sidebar_cal_css.append(
                    'div[data-baseweb="popover"] div[role="gridcell"][data-date]{'
                    'opacity:0.35;cursor:default;}'
                )
                for ad in available_dates:
                    sidebar_cal_css.append(
                        f'div[data-baseweb="popover"] div[role="gridcell"][data-date="{ad}"]'
                        f'{{opacity:1!important;cursor:pointer!important;}}'
                    )
                for vi, vp in enumerate(VERSION_PERIODS):
                    bg_color, text_color = VERSION_COLOR_A if vi % 2 == 0 else VERSION_COLOR_B
                    s = datetime.strptime(vp["start"], "%Y-%m-%d").date()
                    e_date = datetime.strptime(vp["end"], "%Y-%m-%d").date()
                    d = s
                    while d <= e_date:
                        ds = d.strftime("%Y-%m-%d")
                        sidebar_cal_css.append(
                            f'div[data-baseweb="popover"] div[role="gridcell"][data-date="{ds}"]'
                            f'{{background:{bg_color}!important;color:{text_color}!important;'
                            f'font-weight:700!important;border-radius:6px!important;'
                            f'opacity:0.9!important;}}'
                        )
                        d += timedelta(days=1)
                sidebar_cal_css.append(
                    'div[data-baseweb="popover"] div[role="gridcell"][data-overflow]{'
                    'opacity:0.25!important;pointer-events:none!important;}'
                )
                st.markdown(f'<style>{" ".join(sidebar_cal_css)}</style>', unsafe_allow_html=True)

                # 版本tooltip映射
                sidebar_ver_map = {}
                for vp in VERSION_PERIODS:
                    s = datetime.strptime(vp["start"], "%Y-%m-%d").date()
                    e_date = datetime.strptime(vp["end"], "%Y-%m-%d").date()
                    s_d = s.strftime("%m/%d")
                    e_d = e_date.strftime("%m/%d")
                    label = f'{vp["name"]}（{s_d}~{e_d}）'
                    d = s
                    while d <= e_date:
                        sidebar_ver_map[d.strftime("%Y-%m-%d")] = label
                        d += timedelta(days=1)
                sidebar_ver_map_js = json.dumps(sidebar_ver_map, ensure_ascii=False)

                components.html(f"""
<script>
(function(){{
  var monthMap = {{
    'January':'一月','February':'二月','March':'三月','April':'四月',
    'May':'五月','June':'六月','July':'七月','August':'八月',
    'September':'九月','October':'十月','November':'十一月','December':'十二月'
  }};
  var weekdayMap = {{
    'Mo':'一','Tu':'二','We':'三','Th':'四','Fr':'五','Sa':'六','Su':'日',
    'Mon':'一','Tue':'二','Wed':'三','Thu':'四','Fri':'五','Sat':'六','Sun':'日'
  }};
  var versionMap = {sidebar_ver_map_js};
  var parentDoc = window.parent.document;

  function safeReplace(el,map){{
    if(!el.children||!el.children.length){{
      var t=el.textContent||'';
      for(var k in map){{if(t.indexOf(k)!==-1&&t.indexOf(map[k])===-1){{el.textContent=t.replace(k,map[k]);return;}}}}
    }}else{{
      for(var i=0;i<el.children.length;i++){{safeReplace(el.children[i],map);}}
      for(var j=0;j<el.childNodes.length;j++){{
        var n=el.childNodes[j];
        if(n.nodeType===3){{var v=n.nodeValue||'';for(var k in map){{if(v.indexOf(k)!==-1&&v.indexOf(map[k])===-1){{n.nodeValue=v.replace(k,map[k]);return;}}}}}}
      }}
    }}
  }}

  function translateAll(){{
    parentDoc.querySelectorAll('div[data-baseweb="popover"]').forEach(function(pop){{
      pop.querySelectorAll('button').forEach(function(btn){{safeReplace(btn,monthMap);}});
      pop.querySelectorAll('[role="option"],li').forEach(function(item){{safeReplace(item,monthMap);}});
      var thead=pop.querySelector('thead');
      if(thead){{thead.querySelectorAll('*').forEach(function(el){{if(!el.children.length){{var t=(el.textContent||'').trim();if(weekdayMap[t])el.textContent=weekdayMap[t];}}}});}}
    }});
  }}

  function labelAllDates(){{
    var mEN=['January','February','March','April','May','June','July','August','September','October','November','December'];
    var mCN=['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'];
    parentDoc.querySelectorAll('div[data-baseweb="popover"]').forEach(function(pop){{
      var cells=pop.querySelectorAll('div[role="gridcell"]');
      if(!cells.length) return;
      var currentYear=null,currentMonth=null;
      var headerText='';
      var cb=pop.querySelectorAll('button[role="combobox"]');
      if(cb.length){{cb.forEach(function(b){{headerText+=' '+(b.textContent||b.getAttribute('aria-label')||'');}});}}
      if(!headerText.trim()){{pop.querySelectorAll('button,select,[role="heading"]').forEach(function(el){{if(!el.closest('table')&&!el.closest('thead')&&!el.closest('[role="grid"]')){{headerText+=' '+(el.textContent||'');}}}});}}
      if(!headerText.trim()){{headerText=(pop.textContent||'').substring(0,150);}}
      var ym=headerText.match(/(\\d{{4}})/);
      if(ym) currentYear=parseInt(ym[1]);
      for(var i=mEN.length-1;i>=0;i--){{if(headerText.toLowerCase().indexOf(mEN[i].toLowerCase())!==-1||headerText.indexOf(mCN[i])!==-1){{currentMonth=i;break;}}}}
      if(currentYear===null||currentMonth===null){{var now=new Date();if(currentYear===null)currentYear=now.getFullYear();if(currentMonth===null)currentMonth=now.getMonth();}}

      var items=[];
      cells.forEach(function(c){{var d=parseInt((c.textContent||'').trim());items.push({{cell:c,day:isNaN(d)?-1:d}});}});
      var f1=-1;for(var i=0;i<items.length;i++){{if(items[i].day===1){{f1=i;break;}}}}
      var f2=-1;if(f1>=0)for(var i=f1+1;i<items.length;i++){{if(items[i].day===1){{f2=i;break;}}}}
      items.forEach(function(it,idx){{
        var cell=it.cell,day=it.day;if(day<1||day>31)return;
        var y=currentYear,m=currentMonth;
        var ov=(f1>=0&&idx<f1)||(f2>=0&&idx>=f2);
        if(f1>=0&&idx<f1){{m--;if(m<0){{m=11;y--;}}}}
        else if(f2>=0&&idx>=f2){{m++;if(m>11){{m=0;y++;}}}}
        var ds=y+'-'+String(m+1).padStart(2,'0')+'-'+String(day).padStart(2,'0');
        cell.setAttribute('data-date',ds);
        if(ov)cell.setAttribute('data-overflow','1');else cell.removeAttribute('data-overflow');
        if(versionMap[ds]){{cell.setAttribute('title',versionMap[ds]);}}else{{cell.removeAttribute('title');}}
      }});
    }});
  }}

  function runAll(){{translateAll();labelAllDates();}}
  var timer=null;
  var obs=new MutationObserver(function(){{clearTimeout(timer);timer=setTimeout(runAll,60);}});
  obs.observe(parentDoc.body,{{childList:true,subtree:true,characterData:true}});
  parentDoc.addEventListener('click',function(e){{var t=e.target;if(t.closest&&t.closest('[data-baseweb="popover"]')){{setTimeout(runAll,50);setTimeout(runAll,150);setTimeout(runAll,300);setTimeout(runAll,500);}}}},true);
  setTimeout(runAll,200);setTimeout(runAll,500);
}})();
</script>
""", height=0)

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

        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
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
                hint_parts.append(f"「{new_group_name}」")
            if date_changed:
                try:
                    selected_formatted = datetime.strptime(current_selected, "%Y-%m-%d").strftime("%m月%d日")
                    hint_parts.append(f"{selected_formatted}")
                except:
                    pass
            if hint_parts:
                st.info(f"✨ 已选择 {' '.join(hint_parts)}")

        if st.button("✨ 查看数据", use_container_width=True, type="primary"):
            st.session_state.confirmed_group = st.session_state.get("selected_group_cache", "")
            
            if current_query_type == "version":
                st.session_state.confirmed_version = st.session_state.get("selected_version_cache", "")
            else:
                st.session_state.confirmed_date = st.session_state.get("selected_date_cache", "")
            
            st.cache_data.clear()
            _set_nonce()
            st.rerun()
        
        # 前一天/后一天快捷按钮（仅每日查询模式）
        if current_query_type == "daily" and available_dates:
            current_date_str = st.session_state.get("confirmed_date", "") or st.session_state.get("selected_date_cache", "")
            if current_date_str:
                sorted_dates = sorted(available_dates)
                try:
                    current_idx = sorted_dates.index(current_date_str)
                except ValueError:
                    current_idx = -1
                
                prev_date = sorted_dates[current_idx - 1] if current_idx > 0 else None
                next_date = sorted_dates[current_idx + 1] if current_idx >= 0 and current_idx < len(sorted_dates) - 1 else None
                
                # 计算当前日期的前一天和后一天（用于tooltip显示）
                current_date_obj = datetime.strptime(current_date_str, "%Y-%m-%d")
                calc_prev_date = (current_date_obj - timedelta(days=1)).strftime("%Y年%m月%d日")
                calc_next_date = (current_date_obj + timedelta(days=1)).strftime("%Y年%m月%d日")
                
                st.markdown("<div style='margin: 0.6rem 0 0.3rem 0;'></div>", unsafe_allow_html=True)
                
                col_prev, col_next = st.columns(2, gap="small")
                
                with col_prev:
                    if prev_date:
                        prev_tooltip = datetime.strptime(prev_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
                        if st.button("←前一天", key="quick_prev_day", use_container_width=True, help=prev_tooltip):
                            st.session_state.confirmed_date = prev_date
                            st.session_state.selected_date_cache = prev_date
                            if "selected_date_input" in st.session_state:
                                del st.session_state["selected_date_input"]
                            st.session_state.confirmed_group = st.session_state.get("selected_group_cache", "")
                            st.cache_data.clear()
                            _set_nonce()
                            st.rerun()
                    else:
                        st.button("←前一天", key="quick_prev_disabled", use_container_width=True, disabled=True, help=f"{calc_prev_date}（无数据）")
                
                with col_next:
                    if next_date:
                        next_tooltip = datetime.strptime(next_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
                        if st.button("后一天→", key="quick_next_day", use_container_width=True, help=next_tooltip):
                            st.session_state.confirmed_date = next_date
                            st.session_state.selected_date_cache = next_date
                            if "selected_date_input" in st.session_state:
                                del st.session_state["selected_date_input"]
                            st.session_state.confirmed_group = st.session_state.get("selected_group_cache", "")
                            st.cache_data.clear()
                            _set_nonce()
                            st.rerun()
                    else:
                        st.button("后一天→", key="quick_next_disabled", use_container_width=True, disabled=True, help=f"{calc_next_date}（无数据）")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0; color: #64748b; font-size: 0.85rem;">
            💡 数据每日自动更新
        </div>
        """, unsafe_allow_html=True)

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
