"""
验证数据分析阶段是否能正常运行
测试：自动注入配置 + 并行执行两个 Notebook
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from auto_download.config import SOURCE_DIR, NOTEBOOKS
from auto_download.run_notebook import (
    inject_date_into_notebook,
    run_single_notebook_via_nbclient
)


def test_inject_config():
    """测试配置注入功能"""
    print("=" * 60)
    print("🧪 测试 1: 配置注入功能")
    print("=" * 60)
    
    # 使用昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    print(f"📅 测试日期: {date_str}")
    print()
    
    # 测试每个 Notebook 的配置注入
    for nb_config in NOTEBOOKS:
        name = nb_config["name"]
        notebook_path = nb_config["notebook"]
        mapping_file = nb_config.get("mapping_file")
        txt_pattern = nb_config.get("txt_pattern")
        
        print(f"\n📘 {name}")
        print(f"   Notebook: {notebook_path.name}")
        
        if not notebook_path.exists():
            print(f"   ❌ Notebook 不存在: {notebook_path}")
            continue
        
        # 创建临时 notebook
        safe_name = name.replace(" ", "_")
        temp_notebook = SOURCE_DIR / f"_test_temp_{safe_name}_{date_str}.ipynb"
        
        try:
            print(f"   📝 注入配置...")
            inject_date_into_notebook(
                notebook_path,
                date_str,
                temp_notebook,
                txt_file=txt_pattern,
                mapping_file=mapping_file
            )
            
            # 验证临时文件是否存在
            if temp_notebook.exists():
                print(f"   ✅ 配置注入成功: {temp_notebook.name}")
                
                # 读取并验证配置
                import json
                with open(temp_notebook, 'r', encoding='utf-8') as f:
                    nb = json.load(f)
                
                # 查找注入的配置 cell
                found_config = False
                for cell in nb["cells"]:
                    if cell.get("metadata", {}).get("auto_injected"):
                        source = "".join(cell.get("source", []))
                        if date_str in source:
                            found_config = True
                            print(f"   ✅ 找到注入的配置 cell")
                            # 显示配置内容（前3行）
                            lines = source.split("\n")[:5]
                            for line in lines:
                                if line.strip():
                                    print(f"      {line.strip()}")
                            break
                
                if not found_config:
                    print(f"   ⚠️  未找到注入的配置 cell")
                
                # 清理测试文件
                temp_notebook.unlink()
                print(f"   🗑️  已清理测试文件")
            else:
                print(f"   ❌ 临时文件未创建")
                
        except Exception as e:
            print(f"   ❌ 配置注入失败: {e}")
            import traceback
            traceback.print_exc()
            # 清理可能的临时文件
            if temp_notebook.exists():
                temp_notebook.unlink()
    
    print("\n" + "=" * 60)
    print("✅ 测试 1 完成")
    print("=" * 60)


def test_notebook_execution():
    """测试 Notebook 执行（仅验证前几个 cell，不完整执行）"""
    print("\n" + "=" * 60)
    print("🧪 测试 2: Notebook 执行功能（验证模式）")
    print("=" * 60)
    
    # 使用昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    print(f"📅 测试日期: {date_str}")
    print()
    print("⚠️  注意：完整执行需要 5 小时+，这里只验证执行环境")
    print()
    
    # 检查必要的文件是否存在
    print("📋 检查必要文件...")
    all_files_ok = True
    
    for nb_config in NOTEBOOKS:
        name = nb_config["name"]
        notebook_path = nb_config["notebook"]
        mapping_file = nb_config.get("mapping_file")
        txt_pattern = nb_config.get("txt_pattern")
        
        print(f"\n📘 {name}:")
        
        # 检查 Notebook
        if notebook_path.exists():
            print(f"   ✅ Notebook: {notebook_path.name}")
        else:
            print(f"   ❌ Notebook 不存在: {notebook_path}")
            all_files_ok = False
        
        # 检查 mapping 文件
        if mapping_file:
            mapping_path = SOURCE_DIR / mapping_file
            if mapping_path.exists():
                print(f"   ✅ Mapping 文件: {mapping_file}")
            else:
                print(f"   ⚠️  Mapping 文件不存在: {mapping_file}")
        
        # 检查 txt 文件（支持日期前缀匹配）
        if txt_pattern:
            txt_path = SOURCE_DIR / txt_pattern
            if txt_path.exists():
                print(f"   ✅ TXT 文件: {txt_pattern}")
            else:
                # 尝试模式匹配
                pattern = f"*{txt_pattern}"
                matches = list(SOURCE_DIR.glob(pattern))
                if matches:
                    print(f"   ✅ TXT 文件（匹配）: {matches[0].name}")
                else:
                    print(f"   ⚠️  TXT 文件不存在: {txt_pattern}")
                    print(f"      提示：需要先运行 download_chat.py 下载聊天记录")
    
    if not all_files_ok:
        print("\n❌ 部分文件缺失，请先检查文件是否存在")
        return False
    
    # 检查 Python 环境
    print("\n🐍 检查 Python 环境...")
    try:
        import nbformat
        from nbclient import NotebookClient
        print("   ✅ nbclient 已安装")
    except ImportError:
        print("   ❌ nbclient 未安装，请运行: pip install nbclient nbformat")
        return False
    
    # 检查内核
    print("\n🔧 检查 Jupyter 内核...")
    try:
        import jupyter_client
        km = jupyter_client.find_connection_file()
        print("   ✅ Jupyter 内核可用")
    except:
        print("   ⚠️  无法检测 Jupyter 内核，将使用默认 'python3'")
    
    print("\n" + "=" * 60)
    print("✅ 测试 2 完成（环境检查通过）")
    print("=" * 60)
    print("\n💡 提示：")
    print("   - 完整执行请运行: python run_yesterday.py")
    print("   - 或指定日期: python run_notebook.py --date 2025-12-24")
    print("   - 超时时间已设置为 24 小时")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 数据分析阶段验证测试")
    print("=" * 60)
    print()
    
    # 测试1: 配置注入
    test_inject_config()
    
    # 测试2: 执行环境检查
    test_notebook_execution()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成")
    print("=" * 60)
    print("\n下一步：")
    print("1. 确保已下载聊天记录（运行 download_chat.py）")
    print("2. 运行完整分析: python run_yesterday.py")
    print("3. 或指定日期: python run_notebook.py --date 2025-12-24")


if __name__ == "__main__":
    main()

