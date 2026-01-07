"""
运行昨天的数据分析
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from auto_download.run_notebook import run_notebook_via_nbclient

if __name__ == "__main__":
    # 计算昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🚀 运行昨天的数据分析")
    print("=" * 60)
    print(f"📅 分析日期: {date_str}")
    print()
    
    # 运行所有 notebook
    success = run_notebook_via_nbclient(date_str, run_all=True)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 执行完成！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 检查输出文件")
        print("2. 使用 save_results.py 保存结果")
        print("3. 推送到 GitHub")
    else:
        print("\n" + "=" * 60)
        print("❌ 执行失败，请检查错误信息")
        print("=" * 60)
        sys.exit(1)

