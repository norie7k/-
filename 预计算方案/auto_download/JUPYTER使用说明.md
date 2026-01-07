# Jupyter Notebook 运行配置说明

## 📋 概述

本方案用于在 Jupyter Notebook 中手动运行 `top5_Q2_group1.ipynb` 和 `top5_Q2_group2.ipynb`，自动更新日期和文件路径配置。

---

## 🔧 配置说明

### 配置文件位置

配置文件：`预计算方案/auto_download/config.py`

### 当前配置

```python
NOTEBOOKS = [
    {
        "name": "地球群1",
        "notebook": SOURCE_DIR / "top5_Q2_group1.ipynb",
        "mapping_file": "mapping地球1.xlsx",
        "txt_pattern": "《欢迎来到地球》测试1群.txt",  # txt 文件名模式
    },
    {
        "name": "地球群2",
        "notebook": SOURCE_DIR / "top5_Q2_group2.ipynb",
        "mapping_file": "mapping地球2.xlsx",
        "txt_pattern": "《欢迎来到地球》测试2群.txt",  # txt 文件名模式
    },
]
```

### 如何修改配置

如果需要修改配置（例如 txt 文件名或 mapping 文件），编辑 `config.py`：

```python
# 修改群2的配置示例
{
    "name": "地球群2",
    "notebook": SOURCE_DIR / "top5_Q2_group2.ipynb",
    "mapping_file": "mapping地球2.xlsx",  # 修改这里
    "txt_pattern": "新的文件名.txt",  # 修改这里
}
```

---

## 🚀 使用步骤

### 步骤 1: 更新 Notebook 配置

运行脚本自动更新两个 Notebook 的日期和文件路径：

#### 方法 A：使用批处理文件（最简单）

**双击运行：**
```
预计算方案\auto_download\prepare_notebooks_for_jupyter.bat
```

#### 方法 B：在 CMD 中运行

```cmd
cd /d "E:\项目\玩家社群分析智能体"
python "预计算方案\auto_download\prepare_notebooks_for_jupyter.py"
```

#### 方法 C：指定日期运行

```cmd
python "预计算方案\auto_download\prepare_notebooks_for_jupyter.py" --date 2025-12-24
```

**脚本会自动：**
- ✅ 更新 `start_time` 和 `end_time`（分析日期范围）
- ✅ 自动查找并更新 `pathtxt`（支持日期前缀匹配，如 `1219《欢迎来到地球》测试1群.txt`）
- ✅ 更新 `MAPPING_FILE`（映射文件路径）

**输出示例：**
```
============================================================
📝 为 Jupyter Notebook 准备配置
============================================================
📅 分析日期: 2025-12-24

📘 地球群1
   Notebook: top5_Q2_group1.ipynb
  📄 找到匹配文件: 1219《欢迎来到地球》测试1群.txt (模式: 《欢迎来到地球》测试1群.txt)
   ✅ 配置已更新

📘 地球群2
   Notebook: top5_Q2_group2.ipynb
  📄 找到匹配文件: 1230《欢迎来到地球》测试2群.txt (模式: 《欢迎来到地球》测试2群.txt)
   ✅ 配置已更新

============================================================
✅ 所有 Notebook 配置已更新完成！
============================================================
```

---

### 步骤 2: 在 Jupyter Notebook 中打开文件

1. **启动 Jupyter Notebook**
   ```cmd
   cd "E:\项目\玩家社群分析智能体\玩家发言整理（供运营侧）\玩家发言总结_版本总结V2-Copy1.0(单日）"
   jupyter notebook
   ```

2. **打开两个 Notebook**
   - 在浏览器中打开 `top5_Q2_group1.ipynb`
   - 在另一个标签页打开 `top5_Q2_group2.ipynb`

3. **验证配置**
   - 检查第一个代码 cell 中的配置：
     ```python
     start_time = "2025-12-24 00:00:00"  # 应该是更新后的日期
     end_time   = "2025-12-25 00:00:00"
     pathtxt    = "1219《欢迎来到地球》测试1群.txt"  # 应该是匹配到的文件
     MAPPING_FILE = "mapping地球1.xlsx"
     ```

---

### 步骤 3: 运行 Notebook

#### 方式 A：逐个运行（推荐，便于观察进度）

1. **群1 Notebook**
   - 点击菜单：`Kernel → Restart & Run All`
   - 或按快捷键：`Ctrl + Shift + Enter`（运行所有 cell）

2. **群2 Notebook**
   - 在另一个标签页中同样操作
   - 可以同时运行两个 Notebook（并行执行）

#### 方式 B：手动运行每个 Cell

- 按顺序运行每个 cell
- 可以观察每个步骤的输出

---

### 步骤 4: 等待执行完成

- ⏱️ **预计时间**：5 小时+（取决于数据量）
- 📊 **进度显示**：终端会显示批处理进度条
- ⚠️ **注意事项**：
  - 不要关闭浏览器标签页
  - 不要关闭终端窗口
  - 确保网络连接稳定（需要调用 API）

---

### 步骤 5: 保存结果

执行完成后，Notebook 会输出 JSON 格式的结果。

#### 方式 A：使用 save_results.py（推荐）

1. **复制输出的 JSON**
   - 从 Notebook 输出中复制所有 JSON 内容

2. **保存群1的结果**
   ```cmd
   python "预计算方案\auto_download\save_results.py" --group 1 --paste
   ```
   - 粘贴 JSON 内容
   - 输入两个空行结束

3. **保存群2的结果**
   ```cmd
   python "预计算方案\auto_download\save_results.py" --group 2 --paste
   ```

4. **推送到 GitHub（可选）**
   ```cmd
   python "预计算方案\auto_download\save_results.py" --group 1 --paste --push
   ```

#### 方式 B：手动保存

- 复制 JSON 内容
- 保存到文件
- 手动推送到 GitHub

---

## 🔍 常见问题

### Q1: 找不到 txt 文件怎么办？

**原因**：txt 文件不存在或文件名不匹配

**解决**：
1. 检查 `SOURCE_DIR` 目录下是否有 txt 文件
2. 检查 `config.py` 中的 `txt_pattern` 是否正确
3. 如果文件名有日期前缀（如 `1219《欢迎来到地球》测试1群.txt`），脚本会自动匹配

### Q2: 配置没有更新？

**检查**：
1. 确认脚本运行成功（看到 ✅ 提示）
2. 在 Jupyter 中刷新页面（F5）
3. 检查 Notebook 文件是否被修改（查看文件修改时间）

### Q3: Notebook 执行失败？

**可能原因**：
1. **ModuleNotFoundError**：缺少依赖包
   ```cmd
   pip install pandas requests openpyxl tqdm nbclient nbformat
   ```

2. **文件不存在**：检查 txt 文件和 mapping 文件是否存在

3. **API 调用失败**：检查网络连接和 API 配置

### Q4: 如何查看执行进度？

- **终端输出**：查看 Jupyter Notebook 启动的终端窗口
- **Notebook 输出**：查看每个 cell 的执行结果
- **进度条**：批处理时会显示进度条

### Q5: 可以同时运行两个 Notebook 吗？

**可以！** 两个 Notebook 是独立的，可以同时运行：
- 在 Jupyter 中打开两个标签页
- 分别运行两个 Notebook
- 它们会并行执行，互不影响

---

## 📝 配置项说明

### Notebook 中会被更新的配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `start_time` | 分析开始时间 | `"2025-12-24 00:00:00"` |
| `end_time` | 分析结束时间 | `"2025-12-25 00:00:00"` |
| `pathtxt` | txt 文件路径 | `"1219《欢迎来到地球》测试1群.txt"` |
| `MAPPING_FILE` | mapping 文件路径 | `"mapping地球1.xlsx"` |

### config.py 中的配置

| 配置项 | 说明 | 位置 |
|--------|------|------|
| `SOURCE_DIR` | Notebook 所在目录 | `config.py` |
| `NOTEBOOKS` | Notebook 配置列表 | `config.py` |
| `txt_pattern` | txt 文件名模式（支持通配符） | `NOTEBOOKS[].txt_pattern` |
| `mapping_file` | mapping 文件名 | `NOTEBOOKS[].mapping_file` |

---

## 🎯 完整工作流程

```
1. 运行更新脚本
   ↓
   prepare_notebooks_for_jupyter.py
   ↓
2. 在 Jupyter 中打开 Notebook
   ↓
   top5_Q2_group1.ipynb
   top5_Q2_group2.ipynb
   ↓
3. 运行所有 Cell
   ↓
   Kernel → Restart & Run All
   ↓
4. 等待执行完成（5小时+）
   ↓
5. 复制 JSON 输出
   ↓
6. 使用 save_results.py 保存
   ↓
7. 推送到 GitHub（可选）
```

---

## 💡 提示

1. **每天运行前**：先运行 `prepare_notebooks_for_jupyter.py` 更新配置
2. **文件命名**：txt 文件支持日期前缀（如 `1219《欢迎来到地球》测试1群.txt`）
3. **并行执行**：两个 Notebook 可以同时运行，节省时间
4. **结果保存**：执行完成后及时保存结果，避免丢失

---

## 📞 需要帮助？

如果遇到问题，检查：
1. 配置文件 `config.py` 是否正确
2. 文件路径是否存在
3. Python 环境是否安装了所有依赖
4. 网络连接是否正常（API 调用需要）



