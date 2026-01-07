"""
解决 Git 冲突并推送
"""
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_cmd(cmd):
    """运行命令"""
    print(f"\n执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, encoding='utf-8')
    return result.returncode == 0

if __name__ == "__main__":
    print("=" * 60)
    print("解决 Git 冲突并推送")
    print("=" * 60)
    
    # 1. 添加解决后的文件
    print("\n1. 标记冲突已解决...")
    success = run_cmd('git add "预计算方案/app.py"')
    
    if not success:
        print("❌ 添加文件失败")
        exit(1)
    
    # 2. 提交
    print("\n2. 提交冲突解决...")
    success = run_cmd('git commit -m "解决冲突，保留最新的CSS样式"')
    
    if not success:
        print("❌ 提交失败")
        exit(1)
    
    # 3. 推送
    print("\n3. 推送到 GitHub...")
    success = run_cmd("git push")
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 完成！")
        print("=" * 60)
        print("\n💡 提示：等待 1-2 分钟后，按 Ctrl+F5 强制刷新浏览器")
    else:
        print("\n" + "=" * 60)
        print("❌ 推送失败")
        print("=" * 60)

