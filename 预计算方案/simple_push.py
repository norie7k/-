"""简单推送脚本"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_cmd(cmd):
    """运行命令并显示输出"""
    print(f"\n执行: {cmd}\n")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, encoding='utf-8')
    return result.returncode

if __name__ == "__main__":
    print("=" * 60)
    print("推送预计算方案/app.py 到 GitHub")
    print("=" * 60)
    
    # 1. 检查状态
    print("\n1. 检查 Git 状态...")
    run_cmd("git status")
    
    # 2. 添加文件
    print("\n2. 添加文件...")
    run_cmd('git add "预计算方案/app.py"')
    
    # 3. 提交
    print("\n3. 提交更改...")
    run_cmd('git commit -m "[更新] 优化侧边栏文字颜色CSS选择器"')
    
    # 4. 推送
    print("\n4. 推送到 GitHub...")
    code = run_cmd("git push")
    
    if code == 0:
        print("\n✅ 推送成功！")
        print("\n请等待 Streamlit Cloud 自动更新（通常需要1-2分钟）")
        print("然后按 Ctrl+F5 强制刷新浏览器")
    else:
        print("\n❌ 推送失败，请检查错误信息")
    
    print("\n" + "=" * 60)

