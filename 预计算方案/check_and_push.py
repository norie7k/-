"""
检查和推送预计算方案文件到 GitHub
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
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result.returncode == 0, result.stdout, result.stderr

def main():
    os.chdir(PROJECT_ROOT)
    
    print("=" * 60)
    print("检查 Git 状态并推送预计算方案")
    print("=" * 60)
    print()
    
    # 1. 检查 Git 状态
    print("1. 检查 Git 状态...")
    success, stdout, stderr = run_cmd("git status")
    
    if not success:
        print("❌ Git 状态检查失败")
        return
    
    # 检查是否有未提交的更改
    if "预计算方案/app.py" in stdout or "modified" in stdout.lower() or "changes not staged" in stdout.lower():
        print("⚠️ 发现未提交的更改")
        
        # 2. 添加文件
        print("\n2. 添加文件到 Git...")
        files_to_add = [
            "预计算方案/app.py",
            "预计算方案/requirements.txt",
        ]
        
        for file in files_to_add:
            if Path(file).exists():
                success, _, _ = run_cmd(f'git add "{file}"')
                if success:
                    print(f"✅ 已添加: {file}")
                else:
                    print(f"❌ 添加失败: {file}")
            else:
                print(f"⚠️ 文件不存在: {file}")
        
        # 3. 提交
        print("\n3. 提交更改...")
        commit_msg = "[更新] 优化侧边栏文字颜色，确保查询条件和日期选择清晰可见"
        success, _, _ = run_cmd(f'git commit -m "{commit_msg}"')
        
        if not success:
            print("❌ 提交失败，可能没有更改需要提交")
        else:
            print("✅ 提交成功")
    
    # 4. 检查是否需要推送
    print("\n4. 检查是否需要推送...")
    success, stdout, _ = run_cmd("git status")
    
    if "Your branch is ahead of" in stdout or "ahead of" in stdout.lower():
        print("⚠️ 发现未推送的提交")
        
        # 5. 推送
        print("\n5. 推送到 GitHub...")
        success, stdout, stderr = run_cmd("git push")
        
        if success:
            print("✅ 推送成功！")
        else:
            print("❌ 推送失败")
            print(f"错误信息: {stderr}")
    else:
        print("✅ 没有需要推送的更改")
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

