# 故事书生成测试指南

## 改进内容

### 1. 完善了 storage_service.py
添加了两个缺失的关键函数：
- `ensure_folder_structure(folder_type)` - 创建本地文件夹结构
- `save_to_supabase(file_path, folder_type)` - 保存文件到Supabase

### 2. 增强了 storybook_gen.py
- 添加了 `_verify_image_in_db()` 函数，在每张图片生成后立即验证数据库存储
- 改进了日志输出，清晰显示链式生成过程：
  - 显示每页使用的角色参考图片
  - 显示每页使用的之前页面参考图片
  - 显示总参考图片数量
  - 区分文生图和图生图模式
- 如果图片未能存储到数据库，立即抛出异常停止流程

### 3. 创建了完整测试脚本
[test_storybook_complete.py](test_storybook_complete.py) 包含：
- 完整的故事书生成流程测试
- 数据库存储验证（检查所有图片是否在 user_images 表中）
- 图片URL获取验证（测试能否通过 asset_id 获取签名URL）
- 链式生成分析（显示每页的参考关系）
- 详细的测试报告

## 运行测试

### 前置条件
1. 确保 `.env` 文件配置正确：
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_service_key  # 注意：使用 SERVICE_KEY，不是 ANON_KEY
GOOGLE_API_KEY=your_google_api_key
```

2. 确保数据库已初始化：
在 Supabase Dashboard 的 SQL Editor 中执行 [database/scripts/01_initial_setup.sql](database/scripts/01_initial_setup.sql)

### 运行测试
```bash
cd backend
python test_storybook_complete.py
```

## 测试流程

测试脚本会按以下顺序执行：

### 阶段1：生成故事书
- 扩充故事内容
- 提取角色信息
- 生成角色图片（每张图片生成后立即验证数据库）
- 生成故事脚本
- 按顺序生成每页图片（每张图片生成后立即验证数据库）

### 阶段2：验证数据库存储
- 查询所有角色图片是否在 `user_images` 表中
- 查询所有页面图片是否在 `user_images` 表中
- 显示文件名和文件大小

### 阶段3：验证URL获取
- 测试能否通过 `asset_id` 获取每张角色图片的签名URL
- 测试能否通过 `asset_id` 获取每张页面图片的签名URL

### 阶段4：验证链式生成
- 分析每页的参考关系
- 显示每页使用的角色图片
- 显示每页引用的之前页面
- 计算预期的参考图片数量

### 最终摘要
- 显示所有角色及其 image_id
- 显示所有页面及其 generated_image_id
- 显示总图片数量

## 链式生成逻辑

故事书生成使用以下链式逻辑：

1. **角色图片**：使用文生图（text-to-image）生成
2. **第一页**：如果有角色，使用角色图片作为参考；否则使用文生图
3. **后续页面**：
   - 使用该页涉及的角色图片作为参考
   - 使用 `reference_page_numbers` 指定的之前页面图片作为参考
   - 所有参考图片一起传给图生图（image-to-image）API

## 数据库结构

### user_images 表
存储所有图片的元数据：
- `id` (UUID) - 图片ID，被 story_data 引用
- `user_id` (UUID) - 用户ID
- `storage_path` (TEXT) - Supabase Storage 路径
- `filename` (TEXT) - 文件名
- `file_size` (BIGINT) - 文件大小
- `mime_type` (TEXT) - MIME类型
- `created_at` (TIMESTAMPTZ) - 创建时间

### user_storybooks 表
存储故事书数据：
- `id` (UUID) - 故事书ID
- `user_id` (UUID) - 用户ID
- `title` (TEXT) - 标题
- `story_data` (JSONB) - 完整的 Story 对象
- `created_at` (TIMESTAMPTZ) - 创建时间

## 故障排查

### 如果图片未能存储到数据库
1. 检查 Supabase 配置是否正确
2. 确保使用的是 SERVICE_KEY（不是 ANON_KEY）
3. 检查 Storage bucket "files" 是否已创建
4. 检查 user_images 表是否已创建

### 如果无法获取图片URL
1. 检查 Storage policies 是否正确配置
2. 确保 SERVICE_KEY 有权限访问 files bucket
3. 检查 storage_path 是否正确

### 如果链式生成失败
1. 检查前面的图片是否都成功生成
2. 检查 reference_page_numbers 是否引用了已生成的页面
3. 查看详细日志了解哪一步失败

## 下一步

如果测试通过，你可以：
1. 修改测试脚本中的 `story_text` 来测试不同的故事
2. 调整 `aspect_ratio` 参数（如 "1:1", "9:16", "16:9"）
3. 将生成的故事保存到 `user_storybooks` 表
4. 在前端展示生成的故事书
