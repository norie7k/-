# 每日自动化流程

## 流程概述

```
┌────────────────────────────────────────────────────────────────┐
│                    每天凌晨 00:05 自动触发                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   步骤 1: 点击脚本自动下载                                       │
│           ├── 地球群1 → 导出 txt                                │
│           └── 地球群2 → 导出 txt                                │
│                          ↓                                     │
│   步骤 2: 自动运行分析（调用 save_result.py）                    │
│           ├── 分析地球群1 → 2025-12-23_地球群1.json              │
│           └── 分析地球群2 → 2025-12-23_地球群2.json              │
│                          ↓                                     │
│   步骤 3: 推送到 GitHub                                         │
│           git add → git commit → git push                      │
│                          ↓                                     │
│   结果: Streamlit 网页可查看历史结果                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 文件说明

| 文件 | 作用 |
|------|------|
| `calibrate.py` | 🔧 坐标校准（首次运行，记录 QQ 界面各按钮位置） |
| `coordinates.json` | 📍 校准后的坐标 |
| `download_chat.py` | 📥 点击脚本（按坐标自动导出聊天记录） |
| `config.py` | ⚙️ 配置（路径、群信息） |
| `full_pipeline.py` | 🔄 **完整流程**（下载→分析→推送） |
| `setup_schedule.py` | ⏰ 设置 Windows 定时任务 |

---

## 使用步骤

### 1️⃣ 安装依赖

```bash
cd E:\项目\玩家社群分析智能体\预计算方案\auto_download
pip install -r requirements.txt
```

### 2️⃣ 校准坐标（首次使用）

```bash
python calibrate.py
```

按提示依次移动鼠标到各个位置，按空格键记录。

### 3️⃣ 配置群信息

编辑 `config.py`，确认以下配置正确：

```python
QQ_GROUPS = [
    {
        "name": "地球群1",
        "txt_file": "1219《欢迎来到地球》测试1群.txt",  # 实际文件名
        "mapping_file": "mapping地球1.xlsx",
    },
    {
        "name": "地球群2", 
        "txt_file": "地球2群.txt",  # 实际文件名
        "mapping_file": "mapping地球2.xlsx",
    },
]
```

### 4️⃣ 测试运行

```bash
# 测试下载（只显示坐标）
python download_chat.py --test

# 测试完整流程（跳过推送）
python full_pipeline.py --skip-push

# 指定日期分析
python full_pipeline.py --date 2025-12-23 --skip-download --skip-push
```

### 5️⃣ 设置定时任务

```bash
python setup_schedule.py
```

创建 Windows 任务计划，每天 00:05 自动运行 `full_pipeline.py`

---

## 命令参数

### full_pipeline.py

```bash
# 完整流程
python full_pipeline.py

# 跳过下载（只分析+推送）
python full_pipeline.py --skip-download

# 跳过推送（只下载+分析）
python full_pipeline.py --skip-push

# 指定日期
python full_pipeline.py --date 2025-12-23
```

### download_chat.py

```bash
# 测试模式
python download_chat.py --test

# 只下载群1
python download_chat.py --group 1

# 下载所有群
python download_chat.py
```

---

## 注意事项

⚠️ **重要**：

1. **电脑需保持开机** - 凌晨运行时不能休眠
2. **QQ 需已登录** - 脚本运行时 QQ 要在线
3. **界面变化需重新校准** - QQ 更新后重新运行 `calibrate.py`
4. **先手动测试** - 确保稳定后再启用定时任务

---

## 分析逻辑

`full_pipeline.py` 调用 `save_result.py` 运行分析，逻辑与 `top5_Q2.ipynb` 一致：

```
聊天记录 txt
    ↓
模型#1 筛选发言（过滤无关内容）
    ↓
模型#2 话题簇分析（识别讨论主题）
    ↓
模型#3 聚合话题（合并相似话题）
    ↓
计算热度排名（Top 5）
    ↓
模型#4 观点分析（提取玩家意见）
    ↓
保存为 JSON
```
