"""
测试 Jupyter Notebook 自动运行
验证 top5_Q2_group1.ipynb 和 top5_Q2_group2.ipynb 能否正确执行
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from auto_download.config import SOURCE_DIR, NOTEBOOKS, CHAT_SAVE_DIR
from auto_download.run_notebook import run_single_notebook_via_nbclient

def check_files():
    """检查必要的文件是否存在"""
    print("=" * 60)
    print("📋 检查文件")
    print("=" * 60)
    
    all_ok = True
    
    # 检查 Notebook 文件
    print("\n1. 检查 Notebook 文件:")
    for nb_config in NOTEBOOKS:
        notebook_path = nb_config["notebook"]
        exists = notebook_path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {nb_config['name']}: {notebook_path.name}")
        if not exists:
            print(f"      路径: {notebook_path}")
            all_ok = False
    
    # 检查 txt 文件（支持模式匹配）
    print("\n2. 检查聊天记录文件:")
    import glob
    for nb_config in NOTEBOOKS:
        txt_pattern = nb_config.get("txt_pattern", "")
        if txt_pattern:
            # 尝试精确匹配
            txt_path = CHAT_SAVE_DIR / txt_pattern
            exists = txt_path.exists()
            
            # 如果精确匹配失败，尝试模式匹配（支持日期前缀）
            if not exists:
                pattern = f"*{txt_pattern}"
                matches = list(CHAT_SAVE_DIR.glob(pattern))
                if matches:
                    exists = True
                    txt_path = matches[0]  # 使用找到的第一个匹配文件
                    print(f"   ✅ {nb_config['name']}: 找到匹配文件 {txt_path.name}")
                else:
                    status = "⚠️"
                    print(f"   {status} {nb_config['name']}: {txt_pattern}")
                    print(f"      路径: {CHAT_SAVE_DIR / txt_pattern}")
                    print(f"      提示: 文件不存在，可能需要先下载聊天记录")
            else:
                status = "✅"
                print(f"   {status} {nb_config['name']}: {txt_pattern}")
        else:
            print(f"   ⚠️ {nb_config['name']}: 未配置 txt_pattern")
    
    # 检查 mapping 文件
    print("\n3. 检查映射文件:")
    for nb_config in NOTEBOOKS:
        mapping_file = nb_config.get("mapping_file", "")
        if mapping_file:
            mapping_path = SOURCE_DIR / mapping_file
            exists = mapping_path.exists()
            status = "✅" if exists else "❌"
            print(f"   {status} {nb_config['name']}: {mapping_file}")
            if not exists:
                print(f"      路径: {mapping_path}")
                all_ok = False
        else:
            print(f"   ⚠️ {nb_config['name']}: 未配置 mapping_file")
    
    return all_ok


def test_notebook_execution(date_str: str = None, group: str = "all"):
    """
    测试 Notebook 执行
    
    Args:
        date_str: 测试日期，默认为昨天
        group: "all"=全部, "1"=群1, "2"=群2
    """
    if date_str is None:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print("\n" + "=" * 60)
    print("🧪 测试 Notebook 执行")
    print("=" * 60)
    print(f"📅 测试日期: {date_str}")
    print(f"👥 测试群组: {group}")
    print()
    
    # 检查依赖
    try:
        import nbformat
        from nbclient import NotebookClient
        print("✅ nbclient 已安装")
    except ImportError:
        print("❌ 需要安装 nbclient: pip install nbclient nbformat")
        return False
    
    # 选择要测试的 notebook
    if group == "all":
        notebooks_to_test = NOTEBOOKS
    elif group in ("1", "group1"):
        notebooks_to_test = [NOTEBOOKS[0]] if len(NOTEBOOKS) > 0 else []
    elif group in ("2", "group2"):
        notebooks_to_test = [NOTEBOOKS[1]] if len(NOTEBOOKS) > 1 else []
    else:
        print(f"❌ 无效的群组: {group}")
        return False
    
    if not notebooks_to_test:
        print("❌ 没有找到要测试的 notebook")
        return False
    
    # 执行测试
    results = []
    for nb_config in notebooks_to_test:
        print(f"\n{'='*60}")
        print(f"📘 测试: {nb_config['name']}")
        print(f"{'='*60}")
        
        # 只测试前几个 cell（不完整执行，避免耗时）
        print("⚠️  注意: 这是完整执行，可能需要较长时间")
        print("   如果只想验证配置，可以按 Ctrl+C 中断")
        print()
        
        try:
            success = run_single_notebook_via_nbclient(nb_config, date_str)
            results.append((nb_config['name'], success))
        except KeyboardInterrupt:
            print("\n⚠️  用户中断")
            results.append((nb_config['name'], False))
        except Exception as e:
            print(f"\n❌ 执行出错: {e}")
            import traceback
            traceback.print_exc()
            results.append((nb_config['name'], False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    all_success = True
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {name}: {status}")
        if not success:
            all_success = False
    
    return all_success


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="测试 Jupyter Notebook 自动运行")
    parser.add_argument("--date", type=str, help="测试日期 (YYYY-MM-DD)，默认为昨天")
    parser.add_argument("--group", type=str, choices=["all", "1", "2", "group1", "group2"],
                       default="all", help="测试哪个群: all(全部), 1(群1), 2(群2)")
    parser.add_argument("--check-only", action="store_true", help="只检查文件，不执行")
    
    args = parser.parse_args()
    
    # 检查文件
    files_ok = check_files()
    
    if args.check_only:
        if files_ok:
            print("\n✅ 所有文件检查通过！")
        else:
            print("\n⚠️  部分文件缺失，请检查配置")
        return
    
    # 执行测试
    if files_ok:
        print("\n✅ 文件检查通过，开始执行测试...")
        success = test_notebook_execution(args.date, args.group)
        
        if success:
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 部分测试失败，请检查错误信息")
            sys.exit(1)
    else:
        print("\n⚠️  文件检查未通过，请先解决文件问题")
        print("\n建议:")
        print("1. 确保聊天记录文件已下载")
        print("2. 确保映射文件存在")
        print("3. 检查 config.py 中的路径配置")
        sys.exit(1)


if __name__ == "__main__":
    main()

