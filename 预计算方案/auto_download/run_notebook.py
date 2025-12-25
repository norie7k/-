"""
自动执行 Jupyter Notebook 分析
自动修改日期参数后执行 top5_Q2.ipynb

使用方法:
    python run_notebook.py                    # 分析昨天的数据
    python run_notebook.py --date 2025-12-24  # 分析指定日期
    python run_notebook.py --use-server       # 连接到本地 Jupyter 服务器执行
"""
import sys
import os
import json
import shutil
import subprocess
import re
import time
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    requests = None

from config import PROJECT_ROOT, SOURCE_DIR, RESULTS_DIR, NOTEBOOK_PATH, NOTEBOOKS

# Jupyter 服务器配置（从浏览器地址栏获取）
# 例如: http://localhost:8888/?token=abc123...
JUPYTER_URL = "http://localhost:8888"
JUPYTER_TOKEN = ""  # 如果设置了 token，填在这里；留空则自动检测


def get_jupyter_token():
    """
    自动获取本地 Jupyter 服务器的 token
    """
    # 尝试从 jupyter 运行时目录获取
    import glob
    runtime_dir = Path.home() / ".local" / "share" / "jupyter" / "runtime"
    if not runtime_dir.exists():
        # Windows 路径
        runtime_dir = Path.home() / "AppData" / "Roaming" / "jupyter" / "runtime"
    
    if runtime_dir.exists():
        json_files = list(runtime_dir.glob("*server*.json")) + list(runtime_dir.glob("jpserver*.json"))
        for jf in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(jf, 'r') as f:
                    data = json.load(f)
                    if 'token' in data:
                        return data.get('url', JUPYTER_URL), data['token']
            except:
                continue
    
    return JUPYTER_URL, JUPYTER_TOKEN


def run_notebook_via_server(date_str: str = None):
    """
    通过 Jupyter REST API 执行 Notebook
    连接到本地已运行的 Jupyter 服务器
    """
    if requests is None:
        print("❌ 需要安装 requests: pip install requests")
        return False
    
    if date_str is None:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🌐 通过 Jupyter REST API 执行 Notebook")
    print("=" * 60)
    print(f"📅 分析日期: {date_str}")
    print(f"📓 Notebook: {NOTEBOOK_PATH.name}")
    print()
    
    # 获取服务器 URL 和 token
    server_url, token = get_jupyter_token()
    print(f"🔗 服务器: {server_url}")
    
    if not token:
        print("⚠️ 未找到 token，尝试无 token 连接...")
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    # 检查服务器是否可用
    try:
        resp = requests.get(f"{server_url}/api", headers=headers, timeout=5)
        if resp.status_code != 200:
            print(f"❌ 无法连接到 Jupyter 服务器: {resp.status_code}")
            print("请确保 Jupyter Notebook 正在运行")
            return False
        print("✅ 已连接到 Jupyter 服务器")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n请先在终端运行: jupyter notebook")
        return False
    
    # 创建注入日期的临时 notebook
    temp_notebook = SOURCE_DIR / f"_temp_auto_{date_str}.ipynb"
    
    print("\n📝 准备 Notebook...")
    try:
        inject_date_into_notebook(NOTEBOOK_PATH, date_str, temp_notebook)
    except Exception as e:
        print(f"❌ 注入日期失败: {e}")
        return False
    
    # 计算相对路径（相对于 Jupyter 服务器根目录）
    # 假设 Jupyter 从项目根目录启动
    try:
        notebook_rel_path = temp_notebook.relative_to(PROJECT_ROOT)
    except ValueError:
        notebook_rel_path = temp_notebook.name
    
    notebook_api_path = str(notebook_rel_path).replace("\\", "/")
    
    print(f"📄 Notebook 路径: {notebook_api_path}")
    print()
    print("🔄 创建 Kernel 并执行...")
    print("   (请在浏览器中查看执行进度)")
    print()
    
    try:
        # 1. 创建一个新的 kernel
        kernel_resp = requests.post(
            f"{server_url}/api/kernels",
            headers=headers,
            json={"name": "python3"},
            timeout=30
        )
        
        if kernel_resp.status_code not in [200, 201]:
            print(f"❌ 创建 Kernel 失败: {kernel_resp.status_code}")
            return False
        
        kernel_id = kernel_resp.json()["id"]
        print(f"✅ Kernel 已创建: {kernel_id[:8]}...")
        
        # 2. 创建一个 session 来执行 notebook
        session_resp = requests.post(
            f"{server_url}/api/sessions",
            headers=headers,
            json={
                "path": notebook_api_path,
                "name": temp_notebook.name,
                "type": "notebook",
                "kernel": {"id": kernel_id, "name": "python3"}
            },
            timeout=30
        )
        
        if session_resp.status_code not in [200, 201]:
            print(f"❌ 创建 Session 失败: {session_resp.status_code}")
            # 清理 kernel
            requests.delete(f"{server_url}/api/kernels/{kernel_id}", headers=headers)
            return False
        
        session_id = session_resp.json()["id"]
        print(f"✅ Session 已创建: {session_id[:8]}...")
        
        # 3. 读取 notebook 内容
        with open(temp_notebook, 'r', encoding='utf-8') as f:
            nb_content = json.load(f)
        
        # 4. 通过 WebSocket 或逐个执行 cell
        print("\n📊 正在执行 cells...")
        print("   (这可能需要较长时间，请耐心等待)")
        
        # 使用 nbconvert 的 execute 预处理器更可靠
        # 这里简化为直接用 API 执行
        
        # 实际上，Jupyter REST API 不直接支持 "Run All"
        # 最可靠的方式是用 WebSocket 连接 kernel 执行
        # 但这比较复杂，我们改用提示用户手动操作
        
        print()
        print("=" * 60)
        print("📌 请在浏览器中完成以下操作:")
        print("=" * 60)
        print()
        print(f"1. 打开: {server_url}/notebooks/{notebook_api_path}")
        print("2. 点击菜单: Kernel → Restart & Run All")
        print("3. 等待所有 cell 执行完成")
        print()
        print("=" * 60)
        
        # 等待用户确认
        input("按 Enter 键确认已完成执行...")
        
        # 5. 清理
        requests.delete(f"{server_url}/api/sessions/{session_id}", headers=headers)
        
        # 保存执行后的 notebook
        output_notebook = SOURCE_DIR / f"top5_Q2_executed_{date_str}.ipynb"
        if temp_notebook.exists():
            shutil.copy(temp_notebook, output_notebook)
            temp_notebook.unlink()
        
        print(f"\n✅ 完成！")
        print(f"📄 输出文件: {output_notebook}")
        return True
        
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        if temp_notebook.exists():
            temp_notebook.unlink()
        return False


def inject_date_into_notebook(notebook_path: Path, date_str: str, output_path: Path, 
                               txt_file: str = None, mapping_file: str = None):
    """
    自动在 Notebook 开头注入日期设置和文件配置
    
    Args:
        notebook_path: 原始 notebook 路径
        date_str: 分析日期
        output_path: 输出的临时 notebook 路径
        txt_file: 聊天记录 txt 文件名（可选）
        mapping_file: 映射文件名（可选）
    """
    # 读取 notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    # 构建时间范围（与你的 notebook 格式一致：end_time 是第二天 00:00:00）
    start_time = f"{date_str} 00:00:00"
    next_day = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    end_time = f"{next_day} 00:00:00"
    
    # 构建注入代码
    inject_lines = [
        "# ========== 自动注入的配置 (请勿手动修改) ==========\n",
        f"# 分析日期: {date_str}\n",
        f'start_time = "{start_time}"\n',
        f'end_time   = "{end_time}"\n',
    ]
    
    # 如果提供了 txt 文件名，也注入
    if txt_file:
        inject_lines.append(f'pathtxt = "{txt_file}"\n')
    
    # 如果提供了 mapping 文件名，也注入
    if mapping_file:
        inject_lines.append(f'MAPPING_FILE = "{mapping_file}"\n')
    
    inject_lines.extend([
        f'print(f"📅 分析日期: {date_str}")\n',
        'print(f"⏰ 时间范围: {start_time} ~ {end_time}")\n',
    ])
    
    if txt_file:
        inject_lines.append('print(f"📄 聊天记录: {pathtxt}")\n')
    
    inject_lines.append("# ========================================================\n")
    
    # 创建日期注入 cell
    date_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"auto_injected": True},
        "outputs": [],
        "source": inject_lines
    }
    
    # 在 notebook 开头插入日期 cell（跳过可能的 import cell）
    # 找到第一个非 import 的代码 cell 之前插入
    insert_pos = 0
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code":
            source = "".join(cell.get("source", []))
            # 如果是 import 语句开头的 cell，继续往后找
            if source.strip().startswith(("import ", "from ")):
                insert_pos = i + 1
            else:
                break
    
    # 插入日期 cell
    nb["cells"].insert(insert_pos, date_cell)
    
    # 同时，尝试替换 notebook 中已有的 start_time, end_time, pathtxt, MAPPING_FILE 赋值
    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and not cell.get("metadata", {}).get("auto_injected"):
            source_lines = cell.get("source", [])
            if isinstance(source_lines, str):
                source_lines = [source_lines]
            
            new_lines = []
            for line in source_lines:
                # 替换各种变量赋值
                if re.match(r'^start_time\s*=\s*["\']', line):
                    new_lines.append(f'# start_time = ...  # 已被自动设置为 {start_time}\n')
                elif re.match(r'^end_time\s*=\s*["\']', line):
                    new_lines.append(f'# end_time = ...  # 已被自动设置为 {end_time}\n')
                elif txt_file and re.match(r'^pathtxt\s*=\s*["\']', line):
                    new_lines.append(f'# pathtxt = ...  # 已被自动设置为 {txt_file}\n')
                elif mapping_file and re.match(r'^MAPPING_FILE\s*=\s*["\']', line):
                    new_lines.append(f'# MAPPING_FILE = ...  # 已被自动设置为 {mapping_file}\n')
                else:
                    new_lines.append(line)
            
            cell["source"] = new_lines
    
    # 保存修改后的 notebook
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    
    print(f"  ✅ 已注入配置: 日期={date_str}")
    if txt_file:
        print(f"               txt={txt_file}")
    if mapping_file:
        print(f"               mapping={mapping_file}")
    return True


def run_single_notebook_via_nbclient(notebook_config: dict, date_str: str):
    """
    使用 nbclient 执行单个 Notebook
    
    Args:
        notebook_config: 包含 name, notebook, mapping_file, txt_pattern 的配置字典
        date_str: 分析日期
    """
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError:
        print("❌ 需要安装 nbclient: pip install nbclient nbformat")
        return False
    
    name = notebook_config["name"]
    notebook_path = notebook_config["notebook"]
    mapping_file = notebook_config.get("mapping_file")
    txt_pattern = notebook_config.get("txt_pattern")
    
    print("-" * 50)
    print(f"📘 {name}")
    print("-" * 50)
    print(f"📓 Notebook: {notebook_path.name}")
    print(f"📁 工作目录: {SOURCE_DIR}")
    
    if not notebook_path.exists():
        print(f"❌ Notebook 不存在: {notebook_path}")
        return False
    
    # 创建临时 notebook（注入配置后的版本）
    safe_name = name.replace(" ", "_")
    temp_notebook = SOURCE_DIR / f"_temp_{safe_name}_{date_str}.ipynb"
    output_notebook = SOURCE_DIR / f"{notebook_path.stem}_executed_{date_str}.ipynb"
    
    print("📝 准备 Notebook...")
    try:
        inject_date_into_notebook(
            notebook_path, 
            date_str, 
            temp_notebook,
            txt_file=txt_pattern,
            mapping_file=mapping_file
        )
    except Exception as e:
        print(f"❌ 注入配置失败: {e}")
        return False
    
    print()
    print(f"🔄 开始执行...")
    print(f"   (可能需要较长时间，请耐心等待)")
    print()
    
    try:
        # 读取注入日期后的 notebook
        with open(temp_notebook, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # 创建客户端并执行
        client = NotebookClient(
            nb,
            timeout=3600,  # 1小时超时
            kernel_name='python3',
            resources={'metadata': {'path': str(SOURCE_DIR)}}
        )
        
        # 切换到源代码目录执行
        original_dir = os.getcwd()
        os.chdir(SOURCE_DIR)
        
        try:
            client.execute()
        finally:
            os.chdir(original_dir)
        
        # 保存执行后的 notebook
        with open(output_notebook, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        # 删除临时文件
        if temp_notebook.exists():
            temp_notebook.unlink()
        
        print(f"✅ {name} 执行成功!")
        print(f"📄 输出文件: {output_notebook}")
        return True
        
    except Exception as e:
        print(f"❌ {name} 执行出错: {e}")
        if temp_notebook.exists():
            temp_notebook.unlink()
        return False


def run_notebook_via_nbclient(date_str: str = None, run_all: bool = True):
    """
    使用 nbclient 直接执行 Notebook（推荐方式）
    不需要 jupyter 命令，只需要安装 nbclient
    
    Args:
        date_str: 分析日期
        run_all: True=运行所有群的notebook, False=只运行默认notebook
    
    pip install nbclient
    """
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError:
        print("❌ 需要安装 nbclient: pip install nbclient nbformat")
        return False
    
    if date_str is None:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🚀 使用 nbclient 执行 Jupyter Notebook")
    print("=" * 60)
    print(f"📅 分析日期: {date_str}")
    print()
    
    if run_all and NOTEBOOKS:
        # 运行所有配置的 notebooks
        results = []
        for nb_config in NOTEBOOKS:
            success = run_single_notebook_via_nbclient(nb_config, date_str)
            results.append((nb_config["name"], success))
            print()
        
        # 汇总结果
        print("=" * 60)
        print("📊 执行结果汇总")
        print("=" * 60)
        all_success = True
        for name, success in results:
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {name}: {status}")
            if not success:
                all_success = False
        
        return all_success
    else:
        # 向后兼容：只运行默认 notebook
        if not NOTEBOOK_PATH.exists():
            print(f"❌ Notebook 不存在: {NOTEBOOK_PATH}")
            return False
        
        default_config = {
            "name": "默认",
            "notebook": NOTEBOOK_PATH,
        }
        return run_single_notebook_via_nbclient(default_config, date_str)


def run_notebook_via_nbconvert(date_str: str = None):
    """
    使用 nbconvert 执行 Notebook（需要安装 jupyter）
    """
    if date_str is None:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("🚀 使用 nbconvert 执行 Jupyter Notebook")
    print("=" * 60)
    print(f"📅 分析日期: {date_str}")
    print(f"📓 Notebook: {NOTEBOOK_PATH.name}")
    print(f"📁 工作目录: {SOURCE_DIR}")
    print()
    
    if not NOTEBOOK_PATH.exists():
        print(f"❌ Notebook 不存在: {NOTEBOOK_PATH}")
        return False
    
    # 创建临时 notebook（注入日期后的版本）
    temp_notebook = SOURCE_DIR / f"_temp_auto_{date_str}.ipynb"
    output_notebook = SOURCE_DIR / f"top5_Q2_executed_{date_str}.ipynb"
    
    print("📝 准备 Notebook...")
    try:
        inject_date_into_notebook(NOTEBOOK_PATH, date_str, temp_notebook)
    except Exception as e:
        print(f"❌ 注入日期失败: {e}")
        return False
    
    print()
    print(f"🔄 开始执行...")
    print(f"   (可能需要较长时间，请耐心等待)")
    print()
    
    try:
        # 使用 nbconvert 执行 notebook
        result = subprocess.run(
            [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--ExecutePreprocessor.timeout=3600",  # 1小时超时
                "--output", output_notebook.name,
                str(temp_notebook)
            ],
            cwd=str(SOURCE_DIR),
            capture_output=True,
            text=True,
            timeout=3700,  # 略大于内部超时
        )
        
        # 删除临时文件
        if temp_notebook.exists():
            temp_notebook.unlink()
        
        if result.returncode == 0:
            print(f"✅ Notebook 执行成功!")
            print(f"📄 输出文件: {output_notebook}")
            return True
        else:
            print(f"❌ Notebook 执行失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:1000]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 执行超时 (超过1小时)")
        if temp_notebook.exists():
            temp_notebook.unlink()
        return False
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        if temp_notebook.exists():
            temp_notebook.unlink()
        return False


def run_notebook(date_str: str = None, method: str = "auto"):
    """
    执行 Jupyter Notebook
    
    Args:
        date_str: 分析日期 (YYYY-MM-DD)，默认为昨天
        method: 执行方式 - "auto", "nbclient", "nbconvert", "server"
    """
    if method == "server":
        return run_notebook_via_server(date_str)
    
    if method == "auto":
        # 优先使用 nbclient（不需要 jupyter 命令）
        try:
            import nbformat
            from nbclient import NotebookClient
            method = "nbclient"
        except ImportError:
            method = "nbconvert"
    
    if method == "nbclient":
        return run_notebook_via_nbclient(date_str)
    else:
        return run_notebook_via_nbconvert(date_str)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动执行 Jupyter Notebook 分析")
    parser.add_argument("--date", type=str, help="分析日期 (YYYY-MM-DD)，默认为昨天")
    parser.add_argument("--method", type=str, choices=["auto", "nbclient", "nbconvert", "server"],
                       default="auto", 
                       help="执行方式: auto(自动), nbclient(推荐), nbconvert, server(连接本地Jupyter服务器)")
    parser.add_argument("--group", type=str, choices=["all", "group1", "group2", "1", "2"],
                       default="all",
                       help="运行哪个群: all(全部), group1/1(群1), group2/2(群2)")
    args = parser.parse_args()
    
    # 处理群选择
    if args.group in ("all",):
        run_all = True
        selected_groups = None
    else:
        run_all = False
        group_idx = 0 if args.group in ("group1", "1") else 1
        selected_groups = [group_idx]
    
    # 运行
    if args.method == "server":
        success = run_notebook(args.date, args.method)
    elif run_all:
        success = run_notebook(args.date, args.method)
    else:
        # 只运行指定的群
        if args.date is None:
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
        else:
            date_str = args.date
        
        print("=" * 60)
        print(f"🚀 运行指定群的 Notebook")
        print("=" * 60)
        print(f"📅 分析日期: {date_str}")
        print()
        
        all_success = True
        for idx in selected_groups:
            if idx < len(NOTEBOOKS):
                nb_config = NOTEBOOKS[idx]
                success = run_single_notebook_via_nbclient(nb_config, date_str)
                if not success:
                    all_success = False
            else:
                print(f"❌ 群索引 {idx} 不存在")
                all_success = False
        
        success = all_success
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 执行完成!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 执行失败，请检查错误信息")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

