"""
自动下载配置文件
"""
from pathlib import Path

# ==================== 路径配置 ====================

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 源代码目录（Jupyter Notebook 所在位置）
SOURCE_DIR = PROJECT_ROOT / "玩家发言整理（供运营侧）" / "玩家发言总结_版本总结V2-Copy1.0(单日）"

# 聊天记录保存目录（下载的 txt 保存到这里）
CHAT_SAVE_DIR = SOURCE_DIR

# 结果保存目录
RESULTS_DIR = PROJECT_ROOT / "预计算方案" / "results"

# ==================== 群配置 ====================

QQ_GROUPS = [
    {
        "name": "地球群1",
        "txt_file": "《欢迎来到地球》测试1群.txt",
        "mapping_file": "mapping地球1.xlsx",
    },
    {
        "name": "地球群2", 
        "txt_file": "地球2群.txt",  # 根据实际文件名修改
        "mapping_file": "mapping地球2.xlsx",  # 根据实际文件名修改
    },
]

# ==================== Jupyter Notebook 配置 ====================

# 要执行的 Notebook 文件（两个群各一个）
NOTEBOOKS = [
    {
        "name": "地球群1",
        "notebook": SOURCE_DIR / "top5_Q2_group1.ipynb",
        "mapping_file": "mapping地球1.xlsx",
        "txt_pattern": "《欢迎来到地球》测试1群.txt",  # 下载后的文件名
    },
    {
        "name": "地球群2",
        "notebook": SOURCE_DIR / "top5_Q2_group2.ipynb",
        "mapping_file": "mapping地球2.xlsx",
        "txt_pattern": "《欢迎来到地球》测试2群.txt",  # 下载后的文件名
    },
]

# 保持向后兼容
NOTEBOOK_PATH = SOURCE_DIR / "top5_Q2.ipynb"

# ==================== 操作等待时间（秒） ====================

WAIT_TIMES = {
    "action": 1.0,           # 普通点击后等待
    "export_dialog": 5.0,    # 等待导出对话框
    "save": 3.0,             # 保存后等待
    "between_groups": 2.0,   # 两个群之间等待
}
