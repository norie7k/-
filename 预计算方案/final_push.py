"""
最终推送：解决冲突并推送完整文件
"""
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_cmd(cmd):
    """运行命令并显示输出"""
    print(f"\n执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, encoding='utf-8')
    if result.returncode != 0:
        print(f"❌ 失败 (返回码: {result.returncode})")
    else:
        print(f"✅ 成功")
    return result.returncode == 0

if __name__ == "__main__":
    print("=" * 60)
    print("最终推送：解决冲突并推送完整文件")
    print("=" * 60)
    
    # 1. 检查状态
    print("\n1. 检查 Git 状态...")
    run_cmd("git status")
    
    # 2. 添加文件
    print("\n2. 添加文件...")
    if not run_cmd('git add "预计算方案/app.py"'):
        print("❌ 添加文件失败")
        exit(1)
    
    # 3. 提交
    print("\n3. 提交更改...")
    if not run_cmd('git commit -m "[修复] 补全app.py文件，解决冲突，添加完整的main函数和入口代码"'):
        print("⚠️ 提交失败，可能没有更改或已经提交")
    
    # 4. 推送
    print("\n4. 推送到 GitHub...")
    if run_cmd("git push"):
        print("\n" + "=" * 60)
        print("✅ 推送成功！")
        print("=" * 60)
        print("\n💡 提示：")
        print("1. 等待 1-2 分钟让 Streamlit Cloud 更新")
        print("2. 按 Ctrl+F5 强制刷新浏览器")
        print("3. 检查网页是否正常显示")
    else:
        print("\n" + "=" * 60)
        print("❌ 推送失败")
        print("=" * 60)
        print("\n请手动执行：")
        print("  git pull")
        print("  git push")

