# 🎮 玩家社群发言分析 H5 Web 应用

基于 AI 的智能话题挖掘与玩家观点洞察平台，将 Jupyter Notebook 中的分析流程转化为可公开访问的 Web 应用。

> **简化版界面**：默认使用 `top5_Q1.ipynb` 中配置的模型和参数，主页只需选择时间范围即可开始分析。

## ✨ 功能特性

- ⏰ **时间范围选择**：灵活选择开始/结束时间（与 `top5_Q1.ipynb` 主循环对应）
- 📤 **文件上传**：支持上传 QQ 群聊天记录和客服映射文件
- 🔥 **热门话题**：自动识别热度 Top 5 话题簇
- 💬 **观点分析**：深入分析玩家观点共识与分歧
- 📊 **可视化报告**：美观的分析结果展示
- 📥 **结果导出**：支持 JSON 和文本格式导出
- ⚡ **快捷选择**：一键选择"昨天全天"、"今天全天"、"最近3天"

## 🚀 快速开始

### 1. 安装依赖

```bash
cd H5包装
pip install -r requirements.txt
```

### 2. 本地运行

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

### 3. 开始分析

界面已简化，**默认使用预配置的模型**：
1. 上传 QQ 群聊天记录 txt 文件
2. 上传客服昵称映射 Excel 文件
3. 选择要分析的**时间范围**（开始时间 → 结束时间）
4. 点击"开始分析"按钮

> 💡 **提示**：时间范围选择对应 `top5_Q1.ipynb` 中的 `start_time` 和 `end_time` 参数

## 📁 项目结构

```
H5包装/
├── app.py                    # Streamlit 主应用
├── analysis_engine.py        # 核心分析引擎
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── README.md                 # 说明文档
├── .streamlit/
│   └── config.toml           # Streamlit 配置
├── prompts/                  # 提示词目录
│   ├── 提示词1.md            # 模型#1：筛选游戏相关发言
│   ├── 2话题分类.md          # 模型#2：话题簇划分
│   ├── 3日聚合.md            # 模型#3：话题簇聚合
│   └── 2话题分类和总结.md    # 模型#4：玩家观点分析
├── data/                     # 数据目录（可选）
└── output/                   # 输出目录
```

## 🌐 部署到公网

### 方案一：Streamlit Cloud（推荐，免费）

1. 将代码推送到 GitHub 仓库

2. 访问 [Streamlit Cloud](https://share.streamlit.io/)

3. 点击 "New app"，选择你的 GitHub 仓库

4. 配置：
   - Main file path: `H5包装/app.py`
   - Python version: 3.10+

5. 点击 "Deploy"

，### 方案二：自建服务器

1. 准备一台云服务器（阿里云、腾讯云等）

2. 安装 Python 3.10+ 和依赖：
```bash
pip install -r requirements.txt
```

3. 使用 screen 或 systemd 后台运行：
```bash
screen -S streamlit
streamlit run app.py --server.port 80 --server.address 0.0.0.0
```

4. 配置域名和 HTTPS（可选）

### 方案三：Docker 部署

1. 创建 Dockerfile：
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. 构建并运行：
```bash
docker build -t player-analysis .
docker run -p 8501:8501 player-analysis
```

## 📝 使用说明

### 输入文件格式

#### 1. QQ 群聊天记录 (.txt)

从 QQ 导出的群聊天记录文件，格式示例：
```
消息分组:我的群组
消息对象:《欢迎来到地球》测试1群

2025-12-17 10:00:01 玩家昵称(123456)
这个游戏好玩吗？

2025-12-17 10:00:30 青瓷游戏客服-xxx(789012)
欢迎来到测试群！
```

#### 2. 客服昵称映射 (.xlsx)

Excel 文件，包含 "昵称映射" 工作表，字段：
- 真实客服：客服真实姓名
- 昵称：客服在群里使用的昵称

### 分析流程（与 top5_Q1.ipynb 一致）

1. **数据预处理**：解析聊天记录，按时间范围筛选，转换为 JSONL 格式
2. **模型#1 筛选**：使用 V3 模型筛选与游戏相关的发言
3. **模型#2 话题簇划分**：使用 V3.1 模型按语义将发言划分为话题簇
4. **模型#3 话题簇聚合**：将相关话题簇聚合为聚合话题簇
5. **热度计算**：计算每个话题簇的热度评分，提取 Top 5
6. **模型#4 观点分析**：对 Top 5 话题进行玩家观点深度分析

## 🔧 配置说明

### 默认配置（与 top5_Q1.ipynb 一致）

`config.py` 文件中的配置已与 `top5_Q1.ipynb` 保持一致：

```python
# API 配置
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DEFAULT_API_KEY = "de91deb0-aae6-46cb-bac0-17ac3b6107f5"

# 模型配置（与 top5_Q1.ipynb 保持一致）
V3_MODEL_ID = "ep-20251020160142-5d7hp"      # 模型#1：筛选游戏相关发言
V3_1_MODEL_ID = "ep-20251020160025-9p5tj"    # 模型#2/3/4：话题簇划分、聚合、观点分析

# 处理参数
BATCH_SIZE = 300
TEMPERATURE = 0.20
MAX_TOKENS = 16384
TIMEOUT_SEC = 600
```

### 高级设置

如需使用自己的 API Key，可在侧边栏的"高级设置"中修改。

### 修改界面主题

编辑 `.streamlit/config.toml` 文件：

```toml
[theme]
primaryColor = "#6366f1"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#f1f5f9"
```

## ⚠️ 注意事项

1. **API 费用**：每次分析会调用多次 AI API，请注意控制成本
2. **处理时间**：大量数据分析可能需要较长时间（1000条数据约需5-10分钟）
3. **数据安全**：聊天记录包含用户隐私，请妥善保管
4. **网络要求**：需要能够访问火山方舟 API

## 🐛 常见问题

### Q: 分析一直卡在某个步骤？
A: 可能是 API 调用超时，检查网络连接和 API Key 是否正确。

### Q: 结果中某些话题没有观点分析？
A: 可能是该话题的对话数据太少，无法进行有效分析。

### Q: 如何处理更大的数据量？
A: 调小 `batch_size` 参数，或分多天进行分析。

## 📞 联系支持

如有问题，请联系开发团队。

## 📄 License

MIT License

