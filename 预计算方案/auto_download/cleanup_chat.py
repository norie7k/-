"""
清理聊天记录脚本
删除今天下载的群聊天记录 txt 文件
"""
import os
from pathlib import Path
from datetime import datetime

# 聊天记录保存目录
CHAT_DIR = Path(r"E:\项目\玩家社群分析智能体\玩家发言整理（供运营侧）\玩家发言总结_版本总结V2-Copy1.0(单日）")

# 要删除的文件名（群聊天记录文件）
FILE_PATTERNS = [
    "《欢迎来到地球》测试1群.txt",
    "《欢迎来到地球》测试2群.txt",
    # 可以添加更多文件名
]


def cleanup():
    """删除聊天记录文件"""
    print("=" * 60)
    print("🗑️ 清理聊天记录文件")
    print(f"⏰ 时间: {datetime.now()}")
    print(f"📁 目录: {CHAT_DIR}")
    print("=" * 60)
    
    if not CHAT_DIR.exists():
        print(f"❌ 目录不存在: {CHAT_DIR}")
        return
    
    deleted = 0
    
    for pattern in FILE_PATTERNS:
        file_path = CHAT_DIR / pattern
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ 已删除: {pattern}")
                deleted += 1
            except Exception as e:
                print(f"  ❌ 删除失败 {pattern}: {e}")
        else:
            print(f"  ⏭️ 文件不存在: {pattern}")
    
    print()
    print(f"✅ 清理完成，删除了 {deleted} 个文件")
    
    # 记录日志
    log_file = Path(__file__).parent / "cleanup_log.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - 删除了 {deleted} 个文件\n")


if __name__ == "__main__":
    cleanup()

