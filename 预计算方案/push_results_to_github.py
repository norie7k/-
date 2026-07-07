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
    print("推送预计算方案 results 到 GitHub（包含 group1 和 group2）")
    print("=" * 60)
    print()

    # 0. 检查是否有未提交的更改
    print("0. 检查 Git 状态...")
    status_res = subprocess.run(
        "git status --porcelain",
        shell=True,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    has_changes = bool(status_res.stdout.strip())

    # 1. 添加 results 目录（包含 group1 和 group2）
    print("\n1. 添加 预计算方案/results 目录到 Git...")
    results_dir = PROJECT_ROOT / "预计算方案" / "results"
    if results_dir.exists():
        # 使用相对路径，避免 Windows 路径问题
        run_cmd(f'git add "预计算方案/results"')
    else:
        print(f"⚠️ 目录不存在: {results_dir}")
        return

    # 2. 提交（如果有更改）
    print("\n2. 提交更改...")
    commit_msg = f"[数据更新] 更新预计算结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    commit_ok = run_cmd(f'git commit -m "{commit_msg}"')

    if not commit_ok and not has_changes:
        print("ℹ️ 没有需要提交的更改")
        return

    # 3. 先拉远程
    print("\n3. 拉取远程更改...")
    pull_ok = run_cmd("git pull --no-rebase")

    if not pull_ok:
        print("\n⚠️ 拉取失败，可能有冲突")
        print("   请手动执行以下步骤：")
        print("   1. git stash")
        print("   2. git pull")
        print("   3. git stash pop")
        print("   4. 解决冲突后: git add . && git commit -m '解决冲突'")
        print("   5. git push")
        return

    # 4. 推送
    print("\n4. 推送到 GitHub...")
    push_ok = run_cmd("git push")

    if push_ok:
        print("\n" + "=" * 60)
        print("✅ 完成！")
        print("=" * 60)

        # 打印本次提交实际包含的文件（不再写死 group1）
        print("\n📊 本次提交包含的文件：")
        diff_res = subprocess.run(
            "git show --name-only --pretty='' HEAD",
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        files = [line.strip() for line in diff_res.stdout.splitlines() if line.strip()]
        for f in files:
            if "results/" in f:
                print("  -", f)

        print("\n💡 Streamlit Cloud 会在几分钟内自动刷新")
        print("   如果未刷新，可以：")
        print("   1. 等待 2-3 分钟")
        print("   2. 在 Streamlit Cloud 控制台点击 'Reboot app'")
        print("   3. 浏览器 Ctrl+F5 强制刷新")
    else:
        print("\n" + "=" * 60)
        print("❌ 推送失败")
        print("=" * 60)
        print("\n可能原因：")
        print("1. 远程有新的提交，需要先解决冲突")
        print("2. 网络问题")
        print("\n建议手动执行：")
        print("  git pull")
        print("  # 如果有冲突，解决冲突后：")
        print("  git add .")
        print("  git commit -m '解决冲突'")
        print("  git push")

if __name__ == "__main__":
    main()
