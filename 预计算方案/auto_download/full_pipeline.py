"""
完整自动化流程
每天凌晨自动执行：

1. 点击脚本下载 2个群的聊天记录 txt
2. 自动执行 Jupyter Notebook 分析
3. 保存结果到 results/ 并推送到 GitHub

使用方法：
  python full_pipeline.py                  # 完整流程
  python full_pipeline.py --skip-download  # 跳过下载，只运行分析
  python full_pipeline.py --skip-push      # 跳过推送
  python full_pipeline.py --date 2025-12-23  # 指定日期
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from config import PROJECT_ROOT, SOURCE_DIR, RESULTS_DIR, QQ_GROUPS


def step1_download_chat():
    """
    步骤1: 自动下载 QQ 群聊天记录
    使用点击脚本自动导出 txt 文件
    """
    print("\n" + "=" * 60)
    print("📥 步骤 1/3: 下载 QQ 群聊天记录")
    print("=" * 60)
    
    download_script = Path(__file__).parent / "download_chat.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(download_script)],
            timeout=300,  # 5分钟超时
            cwd=str(download_script.parent),
        )
        
        if result.returncode == 0:
            print("✅ 下载完成")
            return True
        else:
            print("❌ 下载失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 下载超时")
        return False
    except Exception as e:
        print(f"❌ 下载出错: {e}")
        return False


def step2_run_jupyter_analysis(date_str: str):
    """
    步骤2: 自动执行 Jupyter Notebook 分析
    
    直接执行你的 top5_Q2.ipynb，通过环境变量传递日期
    """
    print("\n" + "=" * 60)
    print(f"📊 步骤 2/3: 执行 Jupyter Notebook ({date_str})")
    print("=" * 60)
    
    # 使用 run_notebook.py 执行
    run_script = Path(__file__).parent / "run_notebook.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(run_script), "--date", date_str],
            timeout=21700,  # 6小时 + 100秒缓冲（覆盖大数据量的情况）
            cwd=str(run_script.parent),
        )
        
        if result.returncode == 0:
            print("✅ Notebook 执行完成")
            return True
        else:
            print("❌ Notebook 执行失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Notebook 执行超时")
        return False
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False


def step2_use_save_result(date_str: str):
    """
    步骤2（备选）: 使用 save_result.py 运行分析
    
    这种方式不执行 Notebook，而是用 Python 脚本复现 Notebook 逻辑
    适合不想修改 Notebook 的情况
    """
    print("\n" + "=" * 60)
    print(f"📊 步骤 2/3: 运行 save_result.py ({date_str})")
    print("=" * 60)
    
    # 为每个群运行分析
    for group in QQ_GROUPS:
        print(f"\n📁 分析: {group['name']}")
        
        txt_file = SOURCE_DIR / group["txt_file"]
        mapping_file = SOURCE_DIR / group["mapping_file"]
        
        if not txt_file.exists():
            print(f"  ⚠️ 跳过 - 聊天记录不存在: {txt_file.name}")
            continue
        
        # 构建时间参数
        start_time = f"{date_str} 00:00:00"
        next_day = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
        end_time = f"{next_day.strftime('%Y-%m-%d')} 00:00:00"
        
        save_script = PROJECT_ROOT / "预计算方案" / "save_result.py"
        
        try:
            result = subprocess.run([
                sys.executable, str(save_script),
                "--txt", str(txt_file),
                "--mapping", str(mapping_file),
                "--start", start_time,
                "--end", end_time,
                "--output", str(RESULTS_DIR / f"{date_str}_{group['name']}.json")
            ], timeout=3600, cwd=str(save_script.parent))
            
            if result.returncode == 0:
                print(f"  ✅ {group['name']} 分析完成")
            else:
                print(f"  ❌ {group['name']} 分析失败")
                
        except Exception as e:
            print(f"  ❌ 出错: {e}")
    
    return True


def step3_push_to_github(date_str: str):
    """
    步骤3: 推送结果到 GitHub
    """
    print("\n" + "=" * 60)
    print("📤 步骤 3/3: 推送到 GitHub")
    print("=" * 60)
    
    os.chdir(PROJECT_ROOT)
    
    commands = [
        ["git", "add", "预计算方案/results/"],
        ["git", "commit", "-m", f"自动添加 {date_str} 分析结果"],
        ["git", "push"]
    ]
    
    for cmd in commands:
        print(f"  → {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            if "nothing to commit" in stdout or "nothing to commit" in stderr:
                print("    (无需提交)")
            elif "Already up to date" in stdout or "Everything up-to-date" in stderr:
                print("    (已是最新)")
            else:
                print(f"    ⚠️ {stderr[:100]}")
    
    print("✅ 推送完成")


def main():
    parser = argparse.ArgumentParser(description="完整自动化流程")
    parser.add_argument("--skip-download", action="store_true", help="跳过下载步骤")
    parser.add_argument("--skip-push", action="store_true", help="跳过推送步骤")
    parser.add_argument("--date", type=str, help="分析日期 (YYYY-MM-DD)，默认为昨天")
    parser.add_argument("--use-script", action="store_true", 
                       help="使用 save_result.py 而不是执行 Notebook")
    args = parser.parse_args()
    
    # 确定分析日期
    if args.date:
        date_str = args.date
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🚀 玩家社群分析 - 每日自动化流程")
    print("=" * 60)
    print(f"⏰ 运行时间: {datetime.now()}")
    print(f"📅 分析日期: {date_str}")
    print(f"📁 结果目录: {RESULTS_DIR}")
    
    # 步骤 1: 下载
    if not args.skip_download:
        step1_download_chat()
    else:
        print("\n⏭️ 跳过下载步骤")
    
    # 步骤 2: 分析
    if args.use_script:
        # 使用 save_result.py（Python 脚本复现 Notebook 逻辑）
        step2_use_save_result(date_str)
    else:
        # 使用 run_notebook.py（直接执行 Notebook）
        step2_run_jupyter_analysis(date_str)
    
    # 步骤 3: 推送
    if not args.skip_push:
        step3_push_to_github(date_str)
    else:
        print("\n⏭️ 跳过推送步骤")
    
    print("\n" + "=" * 60)
    print("🎉 流程完成！")
    print("=" * 60)
    print(f"\n结果已保存到: {RESULTS_DIR}")
    print("网页查看: 运行 streamlit run 预计算方案/app.py")


if __name__ == "__main__":
    main()
