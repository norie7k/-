# Streamlit 推送工作流（app2 + results2）

本目录从 `预计算方案` 中单独抽取 **将 AI 分析结果推送到 Streamlit 网页** 所需的脚本与配置，按用途分类整理。

## 为什么需要预计算？

Streamlit Cloud 免费版有约 **10 分钟** 超时限制，无法在云端跑完完整的大模型分析（通常需数小时）。因此采用：

```
本地 Notebook 分析 → 转换 JSON → 推送到 GitHub → Streamlit 网页只读展示
```

## 目录结构

```
Streamlit推送工作流打包/
├── README.md
├── requirements.txt
├── app2.py                          # Streamlit 网页（V2，读取 results2）
├── push_app2_to_github.py           # 将 app2 + results2 提交并推送到 GitHub
├── convert/
│   ├── convert_daily)TEST.py        # 转换脚本（内嵌粘贴 AI 输出，适合快速测试）
│   └── convert_daily_from_file.py   # 转换脚本（从 input_daily.json 读取，推荐日常使用）
├── .streamlit/
│   └── config.toml                  # Streamlit 主题与服务器配置
└── results2/                        # 网页数据源（按群、按日存储）
    ├── group1/                      # 地球群1
    │   ├── index.json               # 可用日期索引
    │   ├── daily/                   # 每日 JSON（如 2026-06-01.json）
    │   └── version/                 # 版本周期汇总（预留）
    └── group2/                      # 地球群2
        ├── index.json
        ├── daily/
        └── version/
```

## 两步推送流程

### 第 1 步：转换 AI 输出 → `results2` JSON

AI 分析 Notebook（如 `UP_TEST.ipynb`、`top5_Q2_group2.ipynb`）最终应输出 **话题簇列表**，每个元素包含：

- `聚合话题簇`、`日期`、`时间轴`
- `发言玩家总数`、`发言总数`、`热度评分`
- `讨论点列表` → `观点列表` → `代表性玩家发言` / `原文发言`

#### 方式 A：内嵌粘贴（`convert_daily)TEST.py`）

1. 打开 `convert/convert_daily)TEST.py`
2. 将 AI 输出的 Python 列表粘贴到 `input_data = [...]`
3. 设置 `GROUP_ID = "1"` 或 `"2"`
4. 运行：

```bash
cd Streamlit推送工作流打包
python convert/convert_daily)TEST.py
```

#### 方式 B：从文件读取（`convert_daily_from_file.py`，推荐）

1. 将 AI 输出保存为 `input_daily.json`（放在 `convert/` 或脚本同目录）
2. 运行脚本，按提示选择群组
3. 输出写入 `results2/group{N}/daily/{日期}.json`，并更新 `index.json`

转换后的单日 JSON 结构示例：

```json
{
  "group": "地球群2",
  "group_id": "2",
  "date": "2026-06-01",
  "generated_at": "2026-06-02T13:57:59",
  "source": "QQ",
  "clusters": [ /* 话题簇列表 */ ],
  "summary": {
    "total_clusters": 5,
    "total_players": 98,
    "total_messages": 704,
    "top_cluster": "版本更新后游戏卡顿问题反馈"
  }
}
```

### 第 2 步：推送到 GitHub → Streamlit Cloud 自动更新

在 **完整仓库** `玩家社群分析智能体` 根目录下运行（`push_app2_to_github.py` 依赖该 git 结构）：

```bash
cd E:\项目\玩家社群分析智能体
python 预计算方案/push_app2_to_github.py
```

脚本会依次：

1. 确保 `results2/group1`、`results2/group2` 目录结构完整
2. `git add` → `app2.py`、`.streamlit/config.toml`、`results2/`、`requirements.txt`
3. `git commit` → `git pull` → `git push`

推送完成后，Streamlit Cloud 从 GitHub 拉取最新数据。

| 配置项 | 值 |
|--------|-----|
| Repository | `norie7k/-` |
| Branch | `main` |
| Main file path | `预计算方案/app2.py` |
| 数据目录 | `预计算方案/results2/` |

## 本地预览

```bash
cd 预计算方案
pip install -r requirements.txt
streamlit run app2.py
```

`app2.py` 优先读取本地 `results2/`；部署到 Streamlit Cloud 时从 GitHub Raw URL 拉取：

```
https://raw.githubusercontent.com/norie7k/-/main/预计算方案/results2
```

## 与 qun2_main 工作流的关系

| 工作流 | 输出 | 用途 |
|--------|------|------|
| `qun2_main.ipynb`（研发侧） | Excel（按意图分 sheet） | 研发内部分类、话题簇白名单维护 |
| `top5_Q2_*.ipynb`（运营侧） | 话题簇 JSON 列表 | 每日 Top 热点、观点聚合 |
| **本推送流程** | `results2/*.json` | Streamlit 网页对外展示 |

`qun2_main` 的 Excel 输出 **不能** 直接喂给 `convert_daily`；需要先经过运营侧聚合 Notebook 生成符合上述 schema 的 JSON 列表。

## 相关脚本对照

| 文件 | 作用 |
|------|------|
| `convert_daily)TEST.py` | 测试用：AI 输出直接粘贴在脚本内 |
| `convert_daily_from_file.py` | 正式用：从 `input_daily.json` 读取 |
| `convert_daily_output.py` | 从多段 JSON 文本解析并转换（另一种输入格式） |
| `push_app2_to_github.py` | 一键 git 提交推送 app2 + results2 |
| `app2.py` | Streamlit V2 展示页 |
| `app.py` | Streamlit V1（读取 `results/`，旧版） |

## 注意事项

- `convert_daily)TEST.py` 文件名中含 `)`，是历史命名；日常使用建议 `convert_daily_from_file.py`。
- 推送前确认 `results2/group{N}/daily/` 中已有目标日期的 JSON。
- `push_app2_to_github.py` 必须在已初始化的 git 仓库中运行，且需有 GitHub 推送权限。
- 本打包目录中的 `results2/` 仅含 `index.json` 索引示例；完整历史数据仍在原 `预计算方案/results2/` 目录。
