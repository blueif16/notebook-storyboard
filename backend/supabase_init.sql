-- ============================================
-- Supabase 存储和数据库初始化脚本
-- ============================================
-- 用途：创建文件存储 bucket、数据表和访问策略
-- 使用方法：在 Supabase Dashboard 的 SQL Editor 中执行此脚本

-- ============================================
-- 1. 创建 Storage Bucket
-- ============================================

-- 创建 files bucket（私有，需要签名 URL 访问）
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'files',
  'files',
  false,  -- 私有 bucket，需要签名 URL
  52428800,  -- 50MB 文件大小限制
  ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'video/mp4', 'video/quicktime']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 2. 创建数据表
-- ============================================

-- 创建 user_folders 表（存储文件夹结构）
CREATE TABLE IF NOT EXISTS public.user_folders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  folder_name TEXT NOT NULL,
  parent_folder_id UUID REFERENCES public.user_folders(id) ON DELETE CASCADE,
  storage_path TEXT NOT NULL,
  campaign_id TEXT,
  folder_type TEXT CHECK (folder_type IN ('campaign', 'batch')),
  batch_number INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_user_storage_path UNIQUE(user_id, storage_path)
);

-- 创建 user_files 表（存储文件元数据）
CREATE TABLE IF NOT EXISTS public.user_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  folder_id UUID REFERENCES public.user_folders(id) ON DELETE CASCADE,
  storage_path TEXT NOT NULL UNIQUE,
  filename TEXT NOT NULL,
  file_size BIGINT,
  mime_type TEXT,
  batch_number INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_user_file_path UNIQUE(user_id, storage_path)
);

-- 创建 content_generation_tasks 表（存储任务状态）
CREATE TABLE IF NOT EXISTS public.content_generation_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  campaign_id TEXT NOT NULL,
  batch_id TEXT NOT NULL,
  task_type TEXT NOT NULL CHECK (task_type IN ('image', 'video', 'image_to_image')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- ============================================
-- 3. 创建索引（提升查询性能）
-- ============================================

CREATE INDEX IF NOT EXISTS idx_user_folders_user_id ON public.user_folders(user_id);
CREATE INDEX IF NOT EXISTS idx_user_folders_campaign_id ON public.user_folders(campaign_id);
CREATE INDEX IF NOT EXISTS idx_user_folders_storage_path ON public.user_folders(storage_path);

CREATE INDEX IF NOT EXISTS idx_user_files_user_id ON public.user_files(user_id);
CREATE INDEX IF NOT EXISTS idx_user_files_folder_id ON public.user_files(folder_id);
CREATE INDEX IF NOT EXISTS idx_user_files_storage_path ON public.user_files(storage_path);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON public.content_generation_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.content_generation_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_campaign_batch ON public.content_generation_tasks(campaign_id, batch_id);

-- ============================================
-- 4. 创建 Storage Policies（文件访问控制）
-- ============================================

-- 允许 SERVICE_KEY 访问所有文件（用于后端服务）
CREATE POLICY "Service role can manage all files"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'files');

-- 允许认证用户上传自己的文件
CREATE POLICY "Users can upload their own files"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 允许认证用户读取自己的文件
CREATE POLICY "Users can read their own files"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 允许认证用户更新自己的文件
CREATE POLICY "Users can update their own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 允许认证用户删除自己的文件
CREATE POLICY "Users can delete their own files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- ============================================
-- 5. 创建 RLS Policies（行级安全策略）
-- ============================================

-- 启用 RLS
ALTER TABLE public.user_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_generation_tasks ENABLE ROW LEVEL SECURITY;

-- user_folders 表策略
CREATE POLICY "Users can manage their own folders"
ON public.user_folders FOR ALL
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Service role can manage all folders"
ON public.user_folders FOR ALL
TO service_role
USING (true);

-- user_files 表策略
CREATE POLICY "Users can manage their own files"
ON public.user_files FOR ALL
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Service role can manage all files"
ON public.user_files FOR ALL
TO service_role
USING (true);

-- content_generation_tasks 表策略
CREATE POLICY "Users can manage their own tasks"
ON public.content_generation_tasks FOR ALL
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Service role can manage all tasks"
ON public.content_generation_tasks FOR ALL
TO service_role
USING (true);

-- ============================================
-- 6. 创建触发器（自动更新 updated_at）
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_folders_updated_at
BEFORE UPDATE ON public.user_folders
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_files_updated_at
BEFORE UPDATE ON public.user_files
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
BEFORE UPDATE ON public.content_generation_tasks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 完成
-- ============================================
-- 脚本执行完成！
--
-- 下一步：
-- 1. 在 .env 文件中配置 SUPABASE_URL 和 SUPABASE_SERVICE_KEY
-- 2. 确保使用 SERVICE_KEY（不是 ANON_KEY）以绕过 RLS
-- 3. 运行后端服务测试文件上传功能
