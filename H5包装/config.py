"""
配置文件 - 与 top5_Q1.ipynb 保持一致的默认配置
"""
from pathlib import Path

# ============= API 配置 =============
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DEFAULT_API_KEY = "de91deb0-aae6-46cb-bac0-17ac3b6107f5"  # 默认 API Key

# ============= 模型配置（与 top5_Q1.ipynb 保持一致）=============
# 模型#1：筛选游戏相关发言
V3_MODEL_ID = "ep-20251020160142-5d7hp"
# 模型#2/3/4：话题簇划分、聚合、观点分析
V3_1_MODEL_ID = "ep-20251020160025-9p5tj"
# R1 模型（备用）
R1_MODEL_ID = "ep-20251020160103-5n6g2"

# ============= 处理参数（与 top5_Q1.ipynb 保持一致）=============
BATCH_SIZE = 300
SLEEP_BETWEEN = 1   # 每批之间的间隔，防止QPS触发限流
TEMPERATURE = 0.20
MAX_TOKENS = 16384
TIMEOUT_SEC = 600
RETRIES = 2

# ============= 研发人员映射（与 top5_Q1.ipynb 保持一致）=============
DEFAULT_SPEAKER_MAP = {
    "16186514": "peter本尊",
    "1655611808": "运营绾绾",
    "2073820674": "沙利文老师",
    "2726067525": "milissa",
}

# ============= 客服映射文件 =============
DEFAULT_MAPPING_FILE = "mapping地球1.xlsx"

# ============= 路径配置 =============
BASE_DIR = Path(__file__).parent
PROMPT_DIR = BASE_DIR / "prompts"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# 确保目录存在
PROMPT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

