# 预计算方案 · Streamlit 推送说明

将运营侧 Notebook 的分析结果转换后推送到 Streamlit 网页展示。

## 涉及脚本

| 文件 | 作用 |
|------|------|
| `convert_daily)TEST.py` | 将 AI 输出的话题簇列表转为 `results2/group{N}/daily/{日期}.json` |
| `push_app2_to_github.py` | 将 `app2.py` 与 `results2/` 提交并推送到 GitHub，供 Streamlit Cloud 读取 |

## 工作流程

```
UP_TEST.ipynb 产出话题簇列表（merged_top5 / final_result_day）
        ↓
convert_daily)TEST.py（粘贴到 input_data，设置 GROUP_ID）
        ↓
results2/group{N}/daily/{日期}.json
        ↓
push_app2_to_github.py
        ↓
Streamlit Cloud（预计算方案/app2.py）
```

## 第 1 步：转换

1. 打开 `convert_daily)TEST.py`
2. 将 Notebook 输出的列表粘贴到 `input_data = [...]`
3. 设置 `GROUP_ID = "1"`（地球群1）或 `"2"`（地球群2）
4. 运行：

```bash
cd 预计算方案
python "convert_daily)TEST.py"
```

输出写入 `results2/group{N}/daily/{日期}.json`，并更新 `index.json`。

## 第 2 步：推送到 GitHub

在仓库根目录 `玩家社群分析智能体` 下运行：

```bash
python 预计算方案/push_app2_to_github.py
```

## 第 3 步：查看

**本地预览：**

```bash
cd 预计算方案
pip install -r requirements.txt
streamlit run app2.py
```

**Streamlit Cloud 配置：**

| 配置项 | 值 |
|--------|-----|
| Repository | `norie7k/-` |
| Branch | `main` |
| Main file path | `预计算方案/app2.py` |

## 输入数据要求

每个话题簇需包含：

- `聚合话题簇`、`日期`、`时间轴`
- `发言玩家总数`、`发言总数`、`热度评分`
- `讨论点列表` → `观点列表` → `代表性玩家发言` / `原文发言`
