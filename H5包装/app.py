"""
玩家社群发言分析 H5 Web 应用
基于 Streamlit 构建
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import os

# 设置页面配置
st.set_page_config(
    page_title="玩家社群发言分析",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
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
    
    /* 卡片样式 */
    .result-card {
        background: linear-gradient(145deg, #1e293b, #334155);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .cluster-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #a5b4fc;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(165, 180, 252, 0.3);
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
    
    .discussion-point {
        background: rgba(236, 72, 153, 0.1);
        border-left: 4px solid #ec4899;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 0 8px 8px 0;
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
    
    /* 进度条样式 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1, #ec4899);
    }
    
    /* 热度标签 */
    .heat-badge {
        display: inline-block;
        background: linear-gradient(90deg, #f59e0b, #ef4444);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* 日期统计卡片 */
    .stats-overview {
        background: linear-gradient(145deg, #312e81, #3730a3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .stats-overview h2 {
        color: #c7d2fe;
        margin-bottom: 1rem;
    }
    
    /* 加载动画 */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-text {
        animation: pulse 2s infinite;
        color: #818cf8;
    }
</style>

<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'is_analyzing' not in st.session_state:
        st.session_state.is_analyzing = False


def render_header():
    """渲染页面头部"""
    st.markdown('<h1 class="main-title">🎮 玩家社群发言分析</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">基于AI的智能话题挖掘与玩家观点洞察平台</p>', unsafe_allow_html=True)


def render_sidebar():
    """渲染侧边栏 - 简化版，使用默认配置"""
    from config import (
        DEFAULT_API_KEY, V3_MODEL_ID, V3_1_MODEL_ID, 
        BATCH_SIZE, DEFAULT_SPEAKER_MAP
    )
    
    with st.sidebar:
        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. 上传QQ群聊天记录txt文件
        2. 上传客服昵称映射Excel文件
        3. 选择要分析的**时间范围**
        4. 点击"开始分析"按钮
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ 当前配置")
        st.markdown(f"""
        - **V3模型**: `{V3_MODEL_ID[:20]}...`
        - **V3.1模型**: `{V3_1_MODEL_ID[:20]}...`
        - **批处理大小**: {BATCH_SIZE}
        """)
        
        # 高级设置（折叠）
        with st.expander("🔧 高级设置（可选）"):
            api_key = st.text_input(
                "API Key（留空使用默认）",
                value=st.session_state.get('api_key', ''),
                type="password",
                help="如需使用自己的API密钥，请在此输入"
            )
            if api_key:
                st.session_state['api_key'] = api_key
            else:
                st.session_state['api_key'] = DEFAULT_API_KEY
        
        # 使用默认配置
        return {
            'api_key': st.session_state.get('api_key', DEFAULT_API_KEY),
            'v3_model': V3_MODEL_ID,
            'v3_1_model': V3_1_MODEL_ID,
            'batch_size': BATCH_SIZE,
            'speaker_map': DEFAULT_SPEAKER_MAP,
        }


def render_file_upload():
    """渲染文件上传区域"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 聊天记录文件")
        txt_file = st.file_uploader(
            "上传QQ群聊天记录 (.txt)",
            type=['txt'],
            help="从QQ导出的群聊天记录文件"
        )
    
    with col2:
        st.markdown("#### 📋 客服映射文件")
        mapping_file = st.file_uploader(
            "上传客服昵称映射 (.xlsx)",
            type=['xlsx'],
            help="包含客服昵称映射的Excel文件"
        )
    
    return txt_file, mapping_file


def render_time_range_selector(txt_file):
    """渲染时间范围选择器 - 与 top5_Q1.ipynb 主循环对应"""
    st.markdown("#### 📅 选择分析时间范围")
    st.caption("设定要分析的时间范围，对应主循环中的 `start_time` 和 `end_time`")
    
    # 选择输入模式
    input_mode = st.radio(
        "选择时间输入方式",
        ["📆 日期时间选择器", "✏️ 手动输入时间"],
        horizontal=True,
        key="time_input_mode"
    )
    
    if input_mode == "✏️ 手动输入时间":
        # 手动输入模式
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**开始时间**")
            manual_start = st.text_input(
                "开始时间 (格式: YYYY-MM-DD HH:MM:SS)",
                value=st.session_state.get('manual_start', '2025-12-17 00:00:00'),
                key="manual_start_input",
                placeholder="例如: 2025-12-17 00:00:00"
            )
        
        with col2:
            st.markdown("**结束时间**")
            manual_end = st.text_input(
                "结束时间 (格式: YYYY-MM-DD HH:MM:SS)",
                value=st.session_state.get('manual_end', '2025-12-18 00:00:00'),
                key="manual_end_input",
                placeholder="例如: 2025-12-18 00:00:00"
            )
        
        # 验证时间格式
        try:
            datetime.strptime(manual_start, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(manual_end, "%Y-%m-%d %H:%M:%S")
            start_datetime = manual_start
            end_datetime = manual_end
            display_date = manual_start.split(" ")[0]
            st.success(f"✅ 将分析 **{start_datetime}** 至 **{end_datetime}** 的发言数据")
        except ValueError:
            st.error("⚠️ 时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式")
            start_datetime = None
            end_datetime = None
            display_date = None
    else:
        # 日期时间选择器模式
        col1, col2 = st.columns(2)
        
        # 默认日期：昨天
        default_date = datetime.now().date() - timedelta(days=1)
        
        with col1:
            st.markdown("**开始时间**")
            start_date = st.date_input(
                "开始日期",
                value=st.session_state.get('start_date', default_date),
                key="start_date",
                label_visibility="collapsed"
            )
            start_time = st.time_input(
                "开始时间",
                value=datetime.strptime("00:00:00", "%H:%M:%S").time(),
                key="start_time",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**结束时间**")
            end_date = st.date_input(
                "结束日期",
                value=st.session_state.get('end_date', default_date + timedelta(days=1)),
                key="end_date",
                label_visibility="collapsed"
            )
            end_time = st.time_input(
                "结束时间",
                value=datetime.strptime("00:00:00", "%H:%M:%S").time(),
                key="end_time",
                label_visibility="collapsed"
            )
        
        # 组合成完整的时间字符串（与 top5_Q1.ipynb 格式一致）
        start_datetime = f"{start_date} {start_time.strftime('%H:%M:%S')}"
        end_datetime = f"{end_date} {end_time.strftime('%H:%M:%S')}"
        display_date = str(start_date)
        
        # 显示当前选择
        st.info(f"📊 将分析 **{start_datetime}** 至 **{end_datetime}** 的发言数据")
    
    # 快捷选择按钮
    st.markdown("**快捷选择：**")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("📅 昨天全天", use_container_width=True):
            yesterday = datetime.now().date() - timedelta(days=1)
            st.session_state['start_date'] = yesterday
            st.session_state['end_date'] = datetime.now().date()
            st.session_state['manual_start'] = f"{yesterday} 00:00:00"
            st.session_state['manual_end'] = f"{datetime.now().date()} 00:00:00"
            st.rerun()
    
    with quick_col2:
        if st.button("📅 今天全天", use_container_width=True):
            today = datetime.now().date()
            st.session_state['start_date'] = today
            st.session_state['end_date'] = today + timedelta(days=1)
            st.session_state['manual_start'] = f"{today} 00:00:00"
            st.session_state['manual_end'] = f"{today + timedelta(days=1)} 00:00:00"
            st.rerun()
    
    with quick_col3:
        if st.button("📅 最近3天", use_container_width=True):
            st.session_state['start_date'] = datetime.now().date() - timedelta(days=3)
            st.session_state['end_date'] = datetime.now().date()
            st.session_state['manual_start'] = f"{datetime.now().date() - timedelta(days=3)} 00:00:00"
            st.session_state['manual_end'] = f"{datetime.now().date()} 00:00:00"
            st.rerun()
    
    with quick_col4:
        if st.button("📊 示例数据", help="使用内置示例数据进行演示", use_container_width=True):
            st.session_state['use_demo'] = True
            st.rerun()
    
    return {
        'start_time': start_datetime,
        'end_time': end_datetime,
        'date': display_date,  # 用于显示
    }


def render_result(result):
    """渲染分析结果"""
    if result['status'] == 'error':
        st.error(f"❌ 分析失败: {result['error']}")
        return
    
    if result['status'] == 'no_data':
        st.warning(f"⚠️ {result['error']}")
        return
    
    # 统计概览
    st.markdown(f"""
    <div class="stats-overview">
        <h2>📊 {result['date']} 分析报告</h2>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-value">{result['total_messages']}</div>
                <div class="stat-label">原始消息数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{result['filtered_messages']}</div>
                <div class="stat-label">游戏相关发言</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(result['top5_clusters'])}</div>
                <div class="stat-label">热门话题簇</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 热门话题簇详情
    st.markdown("### 🔥 热门话题 Top 5")
    
    for idx, cluster in enumerate(result['top5_clusters'], 1):
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
            
            # 讨论点列表
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
    
    # 导出按钮
    st.markdown("### 📥 导出结果")
    col1, col2 = st.columns(2)
    
    with col1:
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 下载 JSON 格式",
            data=json_str,
            file_name=f"analysis_{result['date']}.json",
            mime="application/json"
        )
    
    with col2:
        # 生成完整报告文本（包含讨论点、玩家观点、代表性发言）
        report_lines = [f"# 玩家社群发言分析报告 - {result['date']}\n\n"]
        report_lines.append(f"## 统计概览\n")
        report_lines.append(f"- 原始消息数: {result['total_messages']}\n")
        report_lines.append(f"- 游戏相关发言: {result['filtered_messages']}\n")
        report_lines.append(f"- 热门话题簇: {len(result['top5_clusters'])}\n\n")
        
        for idx, cluster in enumerate(result['top5_clusters'], 1):
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
            file_name=f"report_{result['date']}.md",
            mime="text/markdown"
        )


def run_analysis(config, txt_file, mapping_file, time_range):
    """执行分析 - 与 top5_Q1.ipynb 主循环对应"""
    from analysis_engine import PlayerCommunityAnalyzer
    from config import API_URL, DEFAULT_SPEAKER_MAP
    import tempfile
    import os
    
    # 使用配置中的研发人员映射
    speaker_map = config.get('speaker_map', DEFAULT_SPEAKER_MAP)
    
    # 保存上传的文件到临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 保存txt文件
        txt_path = os.path.join(tmpdir, "chat.txt")
        with open(txt_path, 'wb') as f:
            f.write(txt_file.getvalue())
        
        # 保存mapping文件
        mapping_path = os.path.join(tmpdir, "mapping.xlsx")
        with open(mapping_path, 'wb') as f:
            f.write(mapping_file.getvalue())
        
        # 获取提示词目录
        current_dir = Path(__file__).parent
        prompt_dir = current_dir / "prompts"
        
        # 如果本地没有提示词，使用原项目的
        if not prompt_dir.exists():
            prompt_dir = Path("玩家发言整理（供运营侧）/玩家发言总结_版本总结V2-Copy1.0(单日）")
        
        # 创建分析器
        analyzer = PlayerCommunityAnalyzer(
            api_url=API_URL,
            api_key=config['api_key'],
            v3_model_id=config['v3_model'],
            v3_1_model_id=config['v3_1_model'],
            prompt_dir=prompt_dir,
        )
        
        # 进度显示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current, total, message):
            progress_bar.progress(current / total)
            status_text.markdown(f'<p class="loading-text">⏳ {message}</p>', unsafe_allow_html=True)
        
        # 执行分析（使用时间范围参数）
        result = analyzer.analyze(
            txt_path=txt_path,
            mapping_file=mapping_path,
            speaker_map=speaker_map,
            start_time=time_range['start_time'],  # 使用时间范围
            end_time=time_range['end_time'],      # 使用时间范围
            batch_size=config['batch_size'],
            progress_callback=progress_callback,
        )
        
        progress_bar.progress(1.0)
        status_text.empty()
        
        return result


def render_demo_mode():
    """渲染演示模式"""
    st.info("🎯 演示模式：显示示例分析结果")
    
    # 示例数据
    demo_result = {
        "date": "2025-12-17",
        "total_messages": 5498,
        "filtered_messages": 3420,
        "status": "success",
        "top5_clusters": [
            {
                "聚合话题簇": "游戏下载与注册时间咨询",
                "日期": "2025-12-17",
                "时间轴": "10:56:30-11:16:04、11:16:28-11:24:30",
                "发言玩家总数": 90,
                "发言总数": 853,
                "热度评分": 2628.55,
                "讨论点列表": [
                    {
                        "讨论点1": "地球游戏测试版下载链接发放时间与注册开放时间",
                        "玩家观点": [
                            "1：多名玩家询问下载链接和注册开放时间，表现出对游戏测试的期待",
                            "2：个别玩家对下午开放下载和注册的时间安排表示接受",
                            "3：少数玩家担心自己时间冲突，询问是否可以延后注册"
                        ],
                        "代表性玩家发言示例": [
                            "啥时候开启注册啊",
                            "我要上课怎么办",
                            "一点50发链接，再等一会会"
                        ]
                    }
                ]
            },
            {
                "聚合话题簇": "殖装系统开局选择讨论",
                "日期": "2025-12-17",
                "时间轴": "13:52:46-14:03:15、14:12:36-14:27:42",
                "发言玩家总数": 60,
                "发言总数": 485,
                "热度评分": 1321.36,
                "讨论点列表": [
                    {
                        "讨论点1": "各类型殖装开局强度与选择策略",
                        "玩家观点": [
                            "1：多名玩家认为肿头龙开局强度高，适合新手使用",
                            "2：多名玩家认为葡萄开局不好用，体验较差",
                            "3：若干玩家推崇巴大蝶为最强殖装"
                        ],
                        "代表性玩家发言示例": [
                            "肿头龙还是强",
                            "感觉葡萄不是很好用",
                            "大蝴蝶永远的神"
                        ]
                    }
                ]
            },
            {
                "聚合话题簇": "见闻点功能询问",
                "日期": "2025-12-17",
                "时间轴": "14:03:37-14:22:37",
                "发言玩家总数": 44,
                "发言总数": 318,
                "热度评分": 784.63,
                "讨论点列表": [
                    {
                        "讨论点1": "见闻点系统的新增功能与用途说明",
                        "玩家观点": [
                            "1：玩家对见闻点系统的新增功能和用途表示好奇",
                            "2：玩家表示看到了相关信息但保留好奇心"
                        ],
                        "代表性玩家发言示例": [
                            "有点好奇见闻点有啥用",
                            "是的，看到了，保留下好奇"
                        ]
                    }
                ]
            }
        ]
    }
    
    render_result(demo_result)


def main():
    """主函数"""
    init_session_state()
    render_header()
    
    # 侧边栏配置（使用默认配置）
    config = render_sidebar()
    
    # 主内容区
    st.markdown("---")
    
    # 检查是否使用演示模式
    if st.session_state.get('use_demo'):
        render_demo_mode()
        if st.button("🔄 返回正常模式"):
            st.session_state['use_demo'] = False
            st.rerun()
        return
    
    # 文件上传
    txt_file, mapping_file = render_file_upload()
    
    # 时间范围选择（核心功能）
    time_range = render_time_range_selector(txt_file)
    
    st.markdown("---")
    
    # 分析按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button(
            "🚀 开始分析",
            disabled=not (txt_file and mapping_file),
            use_container_width=True
        )
    
    # 清除结果按钮（如果有旧结果）
    if st.session_state.analysis_result:
        with col3:
            if st.button("🗑️ 清除结果", use_container_width=True):
                st.session_state.analysis_result = None
                st.rerun()
    
    # 验证配置并执行分析
    if analyze_btn:
        if not txt_file:
            st.warning("⚠️ 请上传聊天记录文件")
        elif not mapping_file:
            st.warning("⚠️ 请上传客服映射文件")
        elif time_range.get('start_time') is None:
            st.warning("⚠️ 请检查时间格式是否正确")
        else:
            # 清除旧结果，防止显示过期数据
            st.session_state.analysis_result = None
            
            with st.spinner("正在分析中，请稍候..."):
                try:
                    result = run_analysis(config, txt_file, mapping_file, time_range)
                    if result:
                        # 在结果中记录实际分析的时间范围
                        result['analyzed_time_range'] = time_range
                        st.session_state.analysis_result = result
                        st.success(f"✅ 分析完成！时间范围: {time_range['start_time']} ~ {time_range['end_time']}")
                except Exception as e:
                    st.error(f"❌ 分析过程出错: {str(e)}")
                    st.session_state.analysis_result = None
    
    # 显示结果
    if st.session_state.analysis_result:
        st.markdown("---")
        # 显示分析的时间范围提示
        analyzed_range = st.session_state.analysis_result.get('analyzed_time_range', {})
        if analyzed_range:
            st.caption(f"📅 以下是 **{analyzed_range.get('start_time', '')}** 至 **{analyzed_range.get('end_time', '')}** 的分析结果")
        render_result(st.session_state.analysis_result)


if __name__ == "__main__":
    main()

