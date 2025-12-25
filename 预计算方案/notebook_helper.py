"""
Jupyter Notebook 辅助函数
在 top5_Q2.ipynb 中导入使用，方便保存结果
"""
import json
from pathlib import Path
from datetime import datetime

# 结果保存目录
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def save_analysis_result(
    merged_top5: list,
    date: str,
    time_range: str,
    total_messages: int,
    filtered_messages: int,
    output_path: str = None
) -> str:
    """
    保存分析结果到 JSON 文件
    
    在 top5_Q2.ipynb 最后添加以下代码即可：
    
    ```python
    from 预计算方案.notebook_helper import save_analysis_result
    
    save_analysis_result(
        merged_top5=merged_top5,
        date="2025-12-23",
        time_range="2025-12-23 00:00:00 ~ 2025-12-24 00:00:00",
        total_messages=len(jsonl_lines01),
        filtered_messages=written_total,
    )
    ```
    """
    result = {
        "status": "success",
        "date": date,
        "time_range": time_range,
        "total_messages": total_messages,
        "filtered_messages": filtered_messages,
        "top5_clusters": merged_top5,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if output_path is None:
        output_path = RESULTS_DIR / f"{date}.json"
    else:
        output_path = Path(output_path)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 结果已保存到: {output_path}")
    print(f"\n下一步：")
    print(f"1. git add {output_path.relative_to(output_path.parent.parent)}")
    print(f'2. git commit -m "添加 {date} 分析结果"')
    print(f"3. git push")
    
    return str(output_path)


def list_saved_results() -> list:
    """列出所有已保存的结果"""
    results = []
    for f in sorted(RESULTS_DIR.glob("*.json"), reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                results.append({
                    "file": f.name,
                    "date": data.get("date"),
                    "total_messages": data.get("total_messages"),
                    "generated_at": data.get("generated_at")
                })
        except:
            pass
    return results


def load_result(date: str) -> dict:
    """加载指定日期的结果"""
    file_path = RESULTS_DIR / f"{date}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"未找到 {date} 的分析结果")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


