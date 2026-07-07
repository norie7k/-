"""
推送 app.py 到 GitHub
"""
from pathlib import Path
from datetime import datetime
import subprocess
import os

PROJECT_ROOT = Path(__file__).parent.parent

def run_cmd(cmd, cwd=None):
    print(f"执行: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    else:
        if result.stdout.strip():
            print(f"输出: {result.stdout}")
    return result.returncode == 0

def main():
    os.chdir(PROJECT_ROOT)

    print("=" * 60)
    print("推送 app.py 到 GitHub")
    print("=" * 60)
    print()

    # 1. 添加 app.py
    print("1. 添加 预计算方案/app.py 到 Git...")
    app_file = PROJECT_ROOT / "预计算方案" / "app.py"
    if app_file.exists():
        run_cmd(f'git add "预计算方案/app.py"')
    else:
        print(f"⚠️ 文件不存在: {app_file}")
        return

    # 2. 提交
    print("\n2. 提交更改...")
    commit_msg = "更新app.py：将量化数据改为报告说明，显示平台信息和热度公式"
    commit_ok = run_cmd(f'git commit -m "{commit_msg}"')

    if not commit_ok:
        print("ℹ️ 没有需要提交的更改")
        return

    # 3. 先拉远程
    print("\n3. 拉取远程更改...")
    pull_ok = run_cmd("git pull --no-rebase")

    if not pull_ok:
        print("\n⚠️ 拉取失败，可能有冲突")
        return

    # 4. 推送
    print("\n4. 推送到 GitHub...")
    push_ok = run_cmd("git push")

    if push_ok:
        print("\n" + "=" * 60)
        print("✅ 完成！app.py 已推送到 GitHub")
        print("=" * 60)
        print("\n💡 Streamlit Cloud 会在几分钟内自动刷新")
    else:
        print("\n" + "=" * 60)
        print("❌ 推送失败")
        print("=" * 60)

if __name__ == "__main__":
    main()

