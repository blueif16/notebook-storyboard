# 数据库管理

本目录包含所有与 Supabase 数据库相关的脚本和迁移文件。

## 目录结构

```
database/
├── scripts/          # 数据库初始化和维护脚本
│   └── 01_initial_setup.sql
├── migrations/       # 数据库迁移文件（版本控制）
└── README.md        # 本文档
```

## Scripts 目录

包含数据库初始化和维护脚本，用于一次性设置或管理任务。

### 01_initial_setup.sql

完整的 Supabase 初始化脚本，包含：
- Storage Bucket 创建
- 数据表创建（user_folders, user_files, content_generation_tasks）
- 索引创建
- Storage Policies（文件访问控制）
- RLS Policies（行级安全策略）
- 触发器（自动更新时间戳）

**使用方法：**
1. 登录 Supabase Dashboard
2. 进入 SQL Editor
3. 复制并执行 `scripts/01_initial_setup.sql` 的内容

## Migrations 目录

用于存放数据库迁移文件，遵循版本控制最佳实践。

**命名规范：**
```
YYYYMMDD_HHMMSS_description.sql
```

**示例：**
```
20260104_120000_add_user_preferences_table.sql
20260104_150000_add_index_to_tasks.sql
```

## 使用指南

### 初次设置

1. 确保已创建 Supabase 项目
2. 获取项目的 URL 和 SERVICE_KEY
3. 在 Supabase Dashboard 的 SQL Editor 中执行 `scripts/01_initial_setup.sql`
4. 在 `.env` 文件中配置：
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_SERVICE_KEY=your_service_key
   ```

### 创建新的迁移

当需要修改数据库结构时：

1. 在 `migrations/` 目录创建新文件
2. 使用时间戳命名：`YYYYMMDD_HHMMSS_description.sql`
3. 编写迁移 SQL（包含 UP 和 DOWN 逻辑）
4. 在 Supabase Dashboard 中执行
5. 提交到版本控制

### 最佳实践

- 所有数据库更改都应通过迁移文件进行
- 迁移文件应该是幂等的（可重复执行）
- 使用 `IF NOT EXISTS` 和 `ON CONFLICT` 避免重复创建
- 为每个迁移添加清晰的注释
- 测试迁移的回滚逻辑

## 数据表说明

### user_folders
存储用户的文件夹结构，支持层级关系。

### user_files
存储文件元数据，关联到 Storage 中的实际文件。

### content_generation_tasks
跟踪内容生成任务的状态（图片、视频生成等）。

## 安全策略

- 启用了 Row Level Security (RLS)
- 用户只能访问自己的数据
- Service Role 拥有完全访问权限
- Storage 文件按用户 ID 隔离
