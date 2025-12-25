"""
推送预计算方案文件到 GitHub
"""
import subprocess
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_cmd(cmd, cwd=None):
    """运行命令"""
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
        print(f"成功: {result.stdout}")
    return result.returncode == 0

def main():
    os.chdir(PROJECT_ROOT)
    
    print("=" * 60)
    print("推送预计算方案到 GitHub")
    print("=" * 60)
    print()
    
    # 1. 添加文件
    files_to_add = [
        "预计算方案/app.py",
        "预计算方案/requirements.txt",
    ]
    
    print("1. 添加文件到 Git...")
    for file in files_to_add:
        if Path(file).exists():
            run_cmd(f'git add "{file}"')
        else:
            print(f"⚠️ 文件不存在: {file}")
    
    # 2. 提交
    print("\n2. 提交更改...")
    commit_msg = "[更新] 优化侧边栏文字颜色，使用更精确的CSS选择器（div[data-baseweb]）"
    run_cmd(f'git commit -m "{commit_msg}"')
    
    # 3. 先拉取远程更改（如果有）
    print("\n3. 拉取远程更改...")
    pull_success = run_cmd("git pull --rebase")
    
    if not pull_success:
        print("⚠️ 拉取时可能有冲突，请手动解决后重试")
        print("   或者使用: git pull 然后解决冲突")
        return
    
    # 4. 推送
    print("\n4. 推送到 GitHub...")
    push_success = run_cmd("git push")
    
    if push_success:
        print("\n" + "=" * 60)
        print("✅ 完成！")
        print("=" * 60)
        print("\n现在可以在 Streamlit Cloud 部署了：")
        print("  - Repository: norie7k/-")
        print("  - Branch: main")
        print("  - Main file path: 预计算方案/app.py")
        print("\n💡 提示：等待 1-2 分钟后，按 Ctrl+F5 强制刷新浏览器")
    else:
        print("\n" + "=" * 60)
        print("❌ 推送失败")
        print("=" * 60)
        print("\n可能的原因：")
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

