# Supabase 配置指南

## 1. 注册账号

1. 访问 https://supabase.com/
2. 点击 "Start your project"
3. 使用 GitHub 账号登录（推荐）或邮箱注册

## 2. 创建项目

1. 点击 "New Project"
2. 填写项目信息：
   - **Name**: `player-analysis` （或你喜欢的名字）
   - **Database Password**: 设置一个强密码（记住它！）
   - **Region**: 选择 `Northeast Asia (Tokyo)` 或 `Southeast Asia (Singapore)`（离中国近）
3. 点击 "Create new project"
4. 等待 1-2 分钟项目创建完成

## 3. 获取连接信息

1. 进入项目后，点击左侧 "Project Settings" (齿轮图标)
2. 点击 "API"
3. 记录以下信息：
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`

## 4. 创建数据库表

1. 点击左侧 "SQL Editor"
2. 点击 "New Query"
3. 复制粘贴以下 SQL 并执行：

```sql
CREATE TABLE analysis_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'pending',
    txt_file_path TEXT,
    mapping_file_path TEXT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    result JSONB,
    error_message TEXT,
    total_messages INTEGER,
    filtered_messages INTEGER,
    processing_time_seconds REAL
);

CREATE INDEX idx_tasks_status ON analysis_tasks(status);
CREATE INDEX idx_tasks_created_at ON analysis_tasks(created_at DESC);

ALTER TABLE analysis_tasks REPLICA IDENTITY FULL;

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_updated_at
    BEFORE UPDATE ON analysis_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

4. 点击 "Run" 执行

## 5. 创建存储桶

1. 点击左侧 "Storage"
2. 点击 "New Bucket"
3. 创建两个桶：
   - **Name**: `uploads` （存放用户上传的文件）
     - Public: **关闭**
   - **Name**: `results` （存放分析结果）
     - Public: **关闭**

4. 设置存储策略（允许上传下载）：

**对 `uploads` 桶添加两个 Policy：**

**Policy 1 - 允许上传：**
   - 点击 `uploads` 桶 → Policies → New Policy → For full customization
   - Policy name: `Allow uploads`
   - Allowed operation: 选择 `INSERT`
   - Target roles: 选择 `anon`
   - Policy definition: `true`
   - 点击 Save

**Policy 2 - 允许下载：**
   - 点击 New Policy → For full customization
   - Policy name: `Allow downloads`
   - Allowed operation: 选择 `SELECT`
   - Target roles: 选择 `anon`
   - Policy definition: `true`
   - 点击 Save

**对 `results` 桶添加一个 Policy：**
   - 点击 `results` 桶 → Policies → New Policy → For full customization
   - Policy name: `Allow downloads`
   - Allowed operation: 选择 `SELECT`
   - Target roles: 选择 `anon`
   - Policy definition: `true`
   - 点击 Save

## 6. 配置完成

现在你有了：
- ✅ Supabase 项目
- ✅ `analysis_tasks` 表（存储任务）
- ✅ `uploads` 桶（存储上传文件）
- ✅ `results` 桶（存储结果文件）

下一步：配置 `config.py` 并运行监听脚本！

