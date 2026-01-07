"""
检查 group2 的 2025-12-31 文件状态
"""
import subprocess
import json
from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).parent.parent

def check_git_status():
    """检查 Git 状态"""
    print("=" * 60)
    print("1. 检查 Git 状态")
    print("=" * 60)
    
    result = subprocess.run(
        ["git", "status", "--porcelain", "预计算方案/results/group2/"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.stdout.strip():
        print("❌ 有未提交的文件：")
        print(result.stdout)
        return False
    else:
        print("✅ 所有文件已提交")
        return True

def check_local_files():
    """检查本地文件"""
    print("\n" + "=" * 60)
    print("2. 检查本地文件")
    print("=" * 60)
    
    files_to_check = [
        "预计算方案/results/group2/2025-12-31.json",
        "预计算方案/results/group2/index.json"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✅ {file_path} 存在")
            # 检查 index.json 是否包含 2025-12-31
            if "index.json" in file_path:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "2025-12-31" in data.get("available_dates", []):
                        print(f"   ✅ index.json 包含 2025-12-31")
                    else:
                        print(f"   ❌ index.json 不包含 2025-12-31")
                        all_exist = False
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def check_github_raw():
    """检查 GitHub Raw URL"""
    print("\n" + "=" * 60)
    print("3. 检查 GitHub Raw URL")
    print("=" * 60)
    
    base_url = "https://raw.githubusercontent.com/norie7k/-/main/预计算方案/results/group2"
    
    urls_to_check = [
        f"{base_url}/index.json",
        f"{base_url}/2025-12-31.json"
    ]
    
    all_ok = True
    for url in urls_to_check:
        try:
            # 添加时间戳避免缓存
            import time
            url_with_cache = f"{url}?t={int(time.time())}"
            response = requests.get(url_with_cache, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {url}")
                data = response.json()
                if "index.json" in url:
                    if "2025-12-31" in data.get("available_dates", []):
                        print(f"   ✅ index.json 包含 2025-12-31")
                    else:
                        print(f"   ❌ index.json 不包含 2025-12-31")
                        all_ok = False
            else:
                print(f"❌ {url} - HTTP {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("\n🔍 检查 group2 的 2025-12-31 数据状态\n")
    
    git_ok = check_git_status()
    local_ok = check_local_files()
    github_ok = check_github_raw()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    
    if git_ok and local_ok and github_ok:
        print("✅ 所有检查通过！")
        print("\n💡 如果 Streamlit 仍未更新，可能是缓存问题：")
        print("   1. Streamlit 应用缓存了 5 分钟（ttl=300）")
        print("   2. 点击侧边栏的 '🔄 刷新数据' 按钮清除缓存")
        print("   3. 或在 Streamlit Cloud 控制台点击 'Reboot app'")
    else:
        print("❌ 发现问题：")
        if not git_ok:
            print("   - 文件未提交，请运行: python 预计算方案/push_results_to_github.py")
        if not local_ok:
            print("   - 本地文件缺失或格式错误")
        if not github_ok:
            print("   - GitHub 上的文件未更新，请确认已推送")

if __name__ == "__main__":
    main()

