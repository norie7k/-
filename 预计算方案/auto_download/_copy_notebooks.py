"""临时脚本：复制 notebook 文件"""
import shutil
from pathlib import Path

source_dir = Path(r"E:\项目\玩家社群分析智能体\玩家发言整理（供运营侧）\玩家发言总结_版本总结V2-Copy1.0(单日）")
src = source_dir / "top5_Q2.ipynb"

if src.exists():
    dst1 = source_dir / "top5_Q2_group1.ipynb"
    dst2 = source_dir / "top5_Q2_group2.ipynb"
    
    shutil.copy(src, dst1)
    print(f"✅ 已创建: {dst1.name}")
    
    shutil.copy(src, dst2)
    print(f"✅ 已创建: {dst2.name}")
    
    print("\n完成！")
else:
    print(f"❌ 源文件不存在: {src}")

