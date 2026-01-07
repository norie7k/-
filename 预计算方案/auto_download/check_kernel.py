"""
检查当前 Python 环境和 Jupyter 内核配置
"""
import sys
import subprocess
from pathlib import Path

print("=" * 60)
print("🔍 检查 Python 环境和内核配置")
print("=" * 60)

# 1. 检查当前 Python 环境
print("\n1️⃣ 当前 Python 环境:")
print(f"   Python 路径: {sys.executable}")
print(f"   Python 版本: {sys.version}")

# 2. 检查是否安装了 pandas
try:
    import pandas as pd
    print(f"   ✅ pandas 已安装: {pd.__version__}")
except ImportError:
    print("   ❌ pandas 未安装")

# 3. 检查 Jupyter 内核列表
print("\n2️⃣ Jupyter 内核列表:")
try:
    result = subprocess.run(
        ["jupyter", "kernelspec", "list"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("   ⚠️ 无法获取内核列表")
except Exception as e:
    print(f"   ⚠️ 检查内核列表失败: {e}")

# 4. 检查当前环境的内核
print("\n3️⃣ 当前环境的内核:")
try:
    result = subprocess.run(
        [sys.executable, "-m", "ipykernel", "install", "--user", "--name", "python3", "--display-name", f"Python ({Path(sys.executable).parent.name})"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("   ✅ 内核已注册")
    else:
        print("   ⚠️ 内核注册失败（可能已存在）")
except Exception as e:
    print(f"   ⚠️ 内核注册失败: {e}")

print("\n" + "=" * 60)
print("💡 建议:")
print("   1. 确保 Jupyter Notebook 使用与脚本相同的 Python 环境")
print("   2. 在 Jupyter 中：Kernel → Change Kernel → 选择正确的内核")
print("   3. 或者在终端运行：jupyter kernelspec list 查看可用内核")
print("=" * 60)

