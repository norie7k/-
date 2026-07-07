"""
推送 app2.py 和 results2 到 GitHub
"""
from pathlib import Path
from datetime import datetime
import subprocess
import os
import json

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS2_DIR = Path(__file__).parent / "results2"

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

def setup_results2_folder():
    """创建 results2 文件夹结构和 index.json"""
    print("\n📁 设置 results2 文件夹结构...")
    
    for group in ["group1", "group2"]:
        daily_dir = RESULTS2_DIR / group / "daily"
        version_dir = RESULTS2_DIR / group / "version"
        daily_dir.mkdir(parents=True, exist_ok=True)
        version_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建 {group}/daily 和 {group}/version")
        
        index_file = RESULTS2_DIR / group / "index.json"
        if not index_file.exists():
            index_data = {
                "group": f"地球群{group[-1]}",
                "group_id": group[-1],
                "available_dates": [],
                "available_versions": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 创建 {group}/index.json")
        else:
            print(f"  ✓ {group}/index.json 已存在")
    
    for group in ["group1", "group2"]:
        for subdir in ["daily", "version"]:
            gitkeep = RESULTS2_DIR / group / subdir / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()

def main():
    os.chdir(PROJECT_ROOT)

    print("=" * 60)
    print("推送 app2.py 和 results2 到 GitHub")
    print("=" * 60)

    # 0. 设置 results2 文件夹
    setup_results2_folder()

    # 1. 添加 app2.py
    print("\n1. 添加 预计算方案/app2.py 到 Git...")
    app_file = PROJECT_ROOT / "预计算方案" / "app2.py"
    if app_file.exists():
        run_cmd('git add "预计算方案/app2.py"')
    else:
        print(f"⚠️ 文件不存在: {app_file}")
        return

    # 2. 添加 .streamlit/config.toml
    print("\n2. 添加 预计算方案/.streamlit/config.toml 到 Git...")
    config_file = PROJECT_ROOT / "预计算方案" / ".streamlit" / "config.toml"
    if config_file.exists():
        run_cmd('git add "预计算方案/.streamlit/config.toml"')
    else:
        print(f"⚠️ 文件不存在: {config_file}")

    # 3. 添加 results2 文件夹
    print("\n3. 添加 预计算方案/results2 到 Git...")
    run_cmd('git add "预计算方案/results2"')

    # 3.5 添加 requirements.txt
    print("\n3.5 添加 预计算方案/requirements.txt 到 Git...")
    req_file = PROJECT_ROOT / "预计算方案" / "requirements.txt"
    if req_file.exists():
        run_cmd('git add "预计算方案/requirements.txt"')

    # 4. 提交
    print("\n4. 提交更改...")
    commit_msg = f"更新app2.py和results2数据 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    commit_ok = run_cmd(f'git commit -m "{commit_msg}"')

    if not commit_ok:
        print("ℹ️ 没有需要提交的更改")
        return

    # 5. 先拉远程
    print("\n5. 拉取远程更改...")
    pull_ok = run_cmd("git pull --no-rebase")

    if not pull_ok:
        print("\n⚠️ 拉取失败，可能有冲突")
        return

    # 6. 推送
    print("\n6. 推送到 GitHub...")
    push_ok = run_cmd("git push")

    if push_ok:
        print("\n" + "=" * 60)
        print("✅ 完成！app2.py 和 results2 已推送到 GitHub")
        print("=" * 60)
        print("\n💡 现在可以在 Streamlit Cloud 部署:")
        print("   Repository: norie7k/-")
        print("   Branch: main")
        print("   Main file path: 预计算方案/app2.py")
    else:
        print("\n" + "=" * 60)
        print("❌ 推送失败")
        print("=" * 60)

if __name__ == "__main__":
    main()
