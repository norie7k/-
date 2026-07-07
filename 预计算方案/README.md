# 预计算方案

将玩家社群 AI 分析结果预计算为 JSON，通过 GitHub 推送到 Streamlit Cloud 展示，规避 Streamlit 免费版约 **10 分钟** 的超时限制。

## 整体架构

```
QQ 群发言 txt
    ↓
UP_TEST.ipynb（运营侧大模型分析）
    ↓  话题簇列表 merged_top5 / final_result_day
convert_daily_from_file.py  或  convert_daily)TEST.py
    ↓  results2/group{N}/daily/{日期}.json
push_app2_to_github.py
    ↓  git push
Streamlit Cloud（app2.py 只读展示）
```

| 阶段 | 位置 | 产出 |
|------|------|------|
| 数据采集 | QQ 群导出 txt + mapping xlsx | 原始发言 |
| AI 分析 | `玩家发言整理（供运营侧）/…/UP_TEST.ipynb` | 话题簇 JSON 列表 |
| 格式转换 | 本目录 `convert_daily_*.py` | `results2/*.json` |
| 网页展示 | 本目录 `app2.py` | Streamlit 可视化 |

## 目录结构

```
预计算方案/
├── README.md                        # 本文件
├── app2.py                          # Streamlit V2 展示页（主推）
├── app.py                           # Streamlit V1 旧版（读取 results/）
├── requirements.txt
├── push_app2_to_github.py           # 一键推送 app2 + results2 到 GitHub
├── convert_daily)TEST.py            # 转换：内嵌粘贴 AI 输出（测试用）
├── convert_daily_from_file.py       # 转换：从 input_daily.json 读取（推荐）
├── convert_daily_output.py          # 转换：从多段 JSON 文本解析
├── convert_version_output.py        # 转换：版本周期汇总
├── check_github_data.py             # 校验 GitHub 上的 results2 数据
├── .streamlit/config.toml           # Streamlit 主题配置
├── results2/                        # V2 数据源（按群、按日）
│   ├── group1/                      # 地球群1
│   │   ├── index.json
│   │   ├── daily/                   # 2026-06-01.json 等
│   │   └── version/
│   └── group2/                      # 地球群2
└── Streamlit推送工作流打包/          # 可单独分发的推送脚本合集
```

## 快速开始

### 前置依赖

```bash
cd 预计算方案
pip install -r requirements.txt
```

分析 Notebook 还需：`pandas`、`openpyxl`、`requests`、`tqdm` 等（见运营侧目录）。

### 第 1 步：运行 AI 分析（UP_TEST.ipynb）

在 `玩家发言整理（供运营侧）/玩家发言总结_版本总结V2-Copy1.0(单日）/UP_TEST.ipynb` 中：

1. 配置 QQ 群 txt、`mapping地球1.xlsx`、时间范围、`GROUP_ID`
2. 依次跑完模型 #1～#4（筛相关 → 分话题 → 日聚合 → 观点分析）
3. 拿到最终变量 **`merged_top5`** 或 **`final_result_day`**（话题簇列表）

每个话题簇应包含：

- `聚合话题簇`、`日期`、`时间轴`
- `发言玩家总数`、`发言总数`、`热度评分`
- `讨论点列表` → `观点列表` → `代表性玩家发言` / `原文发言`

### 第 2 步：转换为 Streamlit JSON

**方式 A（推荐）：从文件读取**

```bash
# 将 Notebook 输出的列表保存为 input_daily.json
cd 预计算方案
python convert_daily_from_file.py
# 按提示选择群组 1 或 2
```

**方式 B（快速测试）：内嵌粘贴**

```bash
# 编辑 convert_daily)TEST.py：
#   1. 将列表粘贴到 input_data = [...]
#   2. 设置 GROUP_ID = "1" 或 "2"
python "convert_daily)TEST.py"
```

输出写入 `results2/group{N}/daily/{日期}.json`，并自动更新 `index.json`。

### 第 3 步：推送到 GitHub

在仓库根目录 `玩家社群分析智能体` 下执行：

```bash
cd E:\项目\玩家社群分析智能体
python 预计算方案/push_app2_to_github.py
```

脚本会 `git add` → `commit` → `pull` → `push` 以下内容：

- `app2.py`、`.streamlit/config.toml`、`requirements.txt`
- `results2/` 全部数据
- `README.md`、转换脚本、`Streamlit推送工作流打包/`

### 第 4 步：查看结果

**本地预览：**

```bash
cd 预计算方案
streamlit run app2.py
```

**Streamlit Cloud：**

| 配置项 | 值 |
|--------|-----|
| Repository | `norie7k/-` |
| Branch | `main` |
| Main file path | `预计算方案/app2.py` |
| 数据目录 | `预计算方案/results2/` |

云端数据地址：

```
https://raw.githubusercontent.com/norie7k/-/main/预计算方案/results2
```

## 转换后的 JSON 结构

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

## 脚本对照

| 文件 | 作用 |
|------|------|
| `convert_daily)TEST.py` | 测试：AI 输出直接粘贴在脚本内 |
| `convert_daily_from_file.py` | 正式：从 `input_daily.json` 读取 |
| `convert_daily_output.py` | 从多段 JSON 文本解析并转换 |
| `convert_version_output.py` | 版本周期汇总转换 |
| `push_app2_to_github.py` | 一键 git 提交推送 |
| `check_github_data.py` | 校验远程 results2 数据完整性 |
| `app2.py` | Streamlit V2 展示页 |
| `app.py` | Streamlit V1（旧版，读取 `results/`） |

## 与其他工作流的关系

| 工作流 | 输出 | 用途 |
|--------|------|------|
| `qun2_main.ipynb`（研发侧） | Excel | 研发内部分类、话题簇白名单 |
| `UP_TEST.ipynb`（运营侧） | 话题簇 JSON 列表 | 每日 Top 热点 + 观点聚合 |
| **本方案** | `results2/*.json` | Streamlit 网页对外展示 |

研发侧 Excel **不能** 直接喂给 `convert_daily`；需先经运营侧 Notebook 生成符合 schema 的 JSON 列表。

## 注意事项

- `convert_daily)TEST.py` 文件名含 `)`，为历史命名，不影响使用。
- `push_app2_to_github.py` 必须在已初始化的 git 仓库根目录运行，且需有 GitHub 推送权限。
- `UP_TEST.ipynb` 中含 API Key，分享或提交前请脱敏。
- 推送前确认 `results2/group{N}/daily/` 中已有目标日期的 JSON。

## 更多文档

- [Streamlit推送工作流打包/README.md](Streamlit推送工作流打包/README.md) — 可单独分发的推送脚本说明
- [STREAMLIT_CLOUD_SETUP.md](STREAMLIT_CLOUD_SETUP.md) — Streamlit Cloud 部署细节
- [流程说明.md](流程说明.md) — 完整三阶段架构
- [使用说明.md](使用说明.md) — V1 旧版（app + results）说明
