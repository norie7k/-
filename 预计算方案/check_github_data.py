"""
检查 GitHub 上是否有最新的数据文件
"""
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def check_remote_file(file_path):
    """检查远程文件是否存在"""
    cmd = f'git ls-remote --exit-code origin HEAD:{file_path}'
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def main():
    print("=" * 60)
    print("检查 GitHub 上的数据文件")
    print("=" * 60)
    print()
    
    files_to_check = [
        "预计算方案/results/group1/daily/2026-01-14.json",
        "预计算方案/results/group2/daily/2026-01-14.json",
        "预计算方案/results/group1/index.json",
        "预计算方案/results/group2/index.json",
    ]
    
    for file_path in files_to_check:
        # 检查本地文件
        local_file = PROJECT_ROOT / file_path.replace("/", "\\")
        local_exists = local_file.exists()
        
        print(f"📄 {file_path}")
        print(f"   本地: {'✅ 存在' if local_exists else '❌ 不存在'}")
        
        # 检查是否在暂存区
        check_staged = subprocess.run(
            f'git diff --cached --name-only | findstr "{file_path.replace("/", chr(92))}"',
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        is_staged = bool(check_staged.stdout.strip())
        print(f"   暂存: {'✅ 已暂存' if is_staged else '❌ 未暂存'}")
        
        # 检查是否已提交但未推送
        check_committed = subprocess.run(
            f'git log --all --oneline -- "{file_path.replace("/", chr(92))}" | findstr /C:"[数据更新]"',
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        is_committed = bool(check_committed.stdout.strip())
        print(f"   提交: {'✅ 已提交' if is_committed else '❌ 未提交'}")
        print()
    
    print("\n💡 如果文件未推送，请运行：")
    print("   python 预计算方案\\push_results_to_github.py")

if __name__ == "__main__":
    main()
