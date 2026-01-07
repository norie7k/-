# Streamlit Cloud 部署指南

## 步骤 1：确保文件已推送到 GitHub

在本地执行：

```bash
cd "E:\项目\玩家社群分析智能体"

# 检查状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "[更新] 补全app.py，添加.streamlit配置"

# 推送
git push
```

## 步骤 2：在 Streamlit Cloud 创建新应用

1. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io/
   - 使用 GitHub 账号登录

2. **创建新应用**
   - 点击右上角的 "New app" 或 "+ New app" 按钮

3. **配置应用**
   - **Repository（仓库）**: `norie7k/-`
   - **Branch（分支）**: `main`
   - **Main file path（主文件路径）**: `预计算方案/app.py`
   - **App URL（应用URL）**: 可以自定义，例如 `预计算方案` 或 `player-analysis`

4. **点击 "Deploy!"（部署）**

## 步骤 3：等待部署完成

- Streamlit Cloud 会自动：
  1. 克隆你的 GitHub 仓库
  2. 安装 `requirements.txt` 中的依赖
  3. 运行 `预计算方案/app.py`
  4. 部署应用

- 通常需要 1-3 分钟

## 步骤 4：验证部署

部署成功后，你会看到：
- ✅ 绿色的 "Running" 状态
- 应用的 URL（例如：`https://预计算方案.streamlit.app`）

点击 URL 打开应用，应该能看到：
- 深色主题背景
- 侧边栏有"查询条件"
- 可以选择社群和日期
- 文字清晰可见

## 故障排除

### 如果部署失败：

1. **检查 requirements.txt**
   - 确保文件存在且格式正确
   - 依赖版本不要太新（避免兼容性问题）

2. **检查主文件路径**
   - 确保路径正确：`预计算方案/app.py`
   - 注意大小写和路径分隔符

3. **查看日志**
   - 在 Streamlit Cloud 界面点击 "Manage app"
   - 查看 "Logs" 标签页的错误信息

4. **常见错误**
   - `ModuleNotFoundError`: 检查 requirements.txt 是否包含所有依赖
   - `FileNotFoundError`: 检查文件路径是否正确
   - `SyntaxError`: 检查 Python 代码是否有语法错误

## 文件结构要求

确保 GitHub 仓库中有以下文件：

```
预计算方案/
├── app.py                    # 主应用文件（必需）
├── requirements.txt          # Python 依赖（必需）
├── .streamlit/
│   └── config.toml          # Streamlit 配置（可选）
└── results/                 # 结果数据目录（可选）
    ├── group1/
    │   └── index.json
    └── group2/
        └── index.json
```

## 更新应用

每次修改代码后：

1. 推送到 GitHub：
   ```bash
   git add .
   git commit -m "更新描述"
   git push
   ```

2. Streamlit Cloud 会自动检测更改并重新部署（通常需要 1-2 分钟）

3. 刷新浏览器查看更新

