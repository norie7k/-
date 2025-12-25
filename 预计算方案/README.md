# 预计算方案

本方案解决 Streamlit Cloud 免费版 10分钟超时限制的问题。

## 工作流程

```
本地 Jupyter Notebook 分析 → 保存结果为 JSON → 推送到 GitHub → 网页查看
```

## 快速开始

### 1. 在 Notebook 中保存结果

在 `top5_Q2.ipynb` 最后添加：

```python
import sys
sys.path.insert(0, r"E:\项目\玩家社群分析智能体")
from 预计算方案.notebook_helper import save_analysis_result

save_analysis_result(
    merged_top5=merged_top5,
    date=start_time.split(" ")[0],
    time_range=f"{start_time} ~ {end_time}",
    total_messages=len(jsonl_lines01),
    filtered_messages=written_total,
)
```

### 2. 推送到 GitHub

```bash
git add 预计算方案/results/
git commit -m "添加分析结果"
git push
```

### 3. 查看结果

本地运行：
```bash
cd 预计算方案
streamlit run app.py
```

或部署到 Streamlit Cloud（主文件：`预计算方案/app.py`）

## 详细说明

请查看 [使用说明.md](使用说明.md)
