"""
配置文件示例
复制此文件为 config.py 并填入你的 Supabase 信息
"""

# ==================== Supabase 配置 ====================
# 从 Supabase 项目设置 > API 获取
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"

# ==================== 本地路径配置 ====================
# 源代码目录（包含 model_classifyV1_Copy1_Copy1.py 等）
SOURCE_CODE_DIR = r"E:\项目\玩家社群分析智能体\玩家发言整理（供运营侧）\玩家发言总结_版本总结V2-Copy1.0(单日）"

# 提示词目录
PROMPTS_DIR = r"E:\项目\玩家社群分析智能体\玩家发言整理（供运营侧）\玩家发言总结_版本总结V2-Copy1.0(单日）"

# 临时文件目录
TEMP_DIR = r"E:\项目\玩家社群分析智能体\自动化分析方案\temp"

# ==================== API 配置 ====================
# 火山引擎 API（与 top5_Q2.ipynb 一致）
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
API_KEY = "de91deb0-aae6-46cb-bac0-17ac3b6107f5"
V3_MODEL_ID = "ep-20251020160142-5d7hp"
V3_1_MODEL_ID = "ep-20251020160025-9p5tj"

# ==================== 分析参数 ====================
BATCH_SIZE = 300
TEMPERATURE = 0.20
MAX_TOKENS = 16384
TIMEOUT_SEC = 600
RETRIES = 2

# ==================== 研发人员映射 ====================
SPEAKER_MAP = {
    "16186514": "peter本尊",
    "1655611808": "运营绾绾",
    "2073820674": "沙利文老师",
    "2726067525": "milissa",
}

# ==================== 监听配置 ====================
# 轮询间隔（秒）
POLL_INTERVAL = 10


