# 自动化分析方案

## 方案概述

用户在公网网页提交分析请求 → 自动传到本地电脑 → 本地自动跑分析 → 结果返回网页显示

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit 网页 │     │    Supabase     │     │   你的本地电脑   │
│                 │     │   (免费云数据库)  │     │                 │
│  用户提交请求    │ ──→ │  存储待处理任务  │ ←── │  监听脚本自动拉取│
│                 │     │                 │     │       ↓         │
│  显示结果 ←───── │ ←── │  存储分析结果   │ ←── │  自动跑分析      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 工作流程

1. 用户在网页选择日期范围 → 上传 txt 文件 → 点击"提交分析请求"
2. 文件上传到 Supabase Storage，任务信息写入数据库（状态：pending）
3. 你本地的监听脚本检测到新任务
4. 自动下载文件 → 运行分析
5. 结果上传到 Supabase（状态：completed）
6. 网页检测到结果 → 自动显示给用户

## 成本

| 组件 | 成本 |
|------|------|
| Supabase 免费版 | $0 |
| Streamlit Cloud | $0 |
| 本地监听脚本 | $0 |
| **总计** | **免费** |

## 文件结构

```
自动化分析方案/
├── README.md              # 本说明文件
├── config.py              # 配置文件（Supabase 连接信息）
├── task_worker.py         # 本地监听脚本（后台运行）
├── supabase_client.py     # Supabase 操作封装
├── requirements.txt       # 依赖
└── setup_supabase.md      # Supabase 配置指南
```

## 快速开始

### 第一步：注册 Supabase

1. 访问 https://supabase.com/
2. 点击 "Start your project"
3. 使用 GitHub 登录
4. 创建新项目（免费）

### 第二步：配置数据库

参考 `setup_supabase.md` 创建所需的表和存储桶

### 第三步：配置本地环境

1. 复制 `config.example.py` 为 `config.py`
2. 填入你的 Supabase URL 和 Key

### 第四步：运行监听脚本

```bash
cd 自动化分析方案
pip install -r requirements.txt
python task_worker.py
```

### 第五步：部署网页

修改 `H5包装/app.py`，添加任务提交功能

---

## 详细文档

- [Supabase 配置指南](setup_supabase.md)
- [本地监听脚本说明](task_worker.py)
- [网页改造说明](webapp_changes.md)


