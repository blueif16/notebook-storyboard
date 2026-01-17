-- ============================================
-- Supabase 数据库初始化脚本
-- ============================================
-- 用途：创建用户故事书和图片存储
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
  ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'video/mp4']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 2. 创建数据表
-- ============================================

-- 创建 user_images 表（存储图片元数据）
CREATE TABLE IF NOT EXISTS public.user_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  storage_path TEXT NOT NULL UNIQUE,
  filename TEXT NOT NULL,
  file_size BIGINT,
  mime_type TEXT DEFAULT 'image/jpeg',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建 user_storybooks 表（存储用户的故事书）
CREATE TABLE IF NOT EXISTS public.user_storybooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL,
  story_data JSONB NOT NULL,
  source_titles JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. 创建索引（提升查询性能）
-- ============================================

CREATE INDEX IF NOT EXISTS idx_images_user_id ON public.user_images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_storage_path ON public.user_images(storage_path);

CREATE INDEX IF NOT EXISTS idx_storybooks_user_id ON public.user_storybooks(user_id);
CREATE INDEX IF NOT EXISTS idx_storybooks_created_at ON public.user_storybooks(created_at DESC);

-- ============================================
-- 4. 创建 Storage Policies（文件访问控制）
-- ============================================

-- 允许 SERVICE_KEY 访问所有文件（用于后端服务）
CREATE POLICY "Service role can manage all files"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'files');

-- 允许认证用户读取自己的文件
CREATE POLICY "Users can read their own files"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'files' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- 允许认证用户上传自己的文件
CREATE POLICY "Users can upload their own files"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
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
-- 5. 启用 RLS（行级安全策略）
-- ============================================

-- user_images 表
ALTER TABLE public.user_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own images"
ON public.user_images FOR ALL
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Service role can manage all images"
ON public.user_images FOR ALL
TO service_role
USING (true);

-- user_storybooks 表
ALTER TABLE public.user_storybooks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own storybooks"
ON public.user_storybooks FOR ALL
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Service role can manage all storybooks"
ON public.user_storybooks FOR ALL
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

CREATE TRIGGER update_storybooks_updated_at
BEFORE UPDATE ON public.user_storybooks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 完成
-- ============================================
-- 脚本执行完成！
--
-- 数据结构说明：
--
-- 1. user_images 表：存储所有图片的元数据
--    - id: 图片UUID（这个ID会被 story_data 中的 image_id 引用）
--    - storage_path: Supabase Storage 中的路径（如 "user_id/images/filename.jpg"）
--    - 图片实际存储在 Supabase Storage 的 'files' bucket 中
--
-- 2. user_storybooks 表：存储故事书
--    - story_data JSONB 字段存储完整的 Story 对象：
--    {
--      "characters": [
--        {"name": "角色名", "description": "描述", "image_id": "UUID引用user_images.id"}
--      ],
--      "pages": [
--        {
--          "page_number": 1,
--          "plot": "情节描述",
--          "character_names": ["角色1", "角色2"],
--          "reference_page_numbers": [1, 2],
--          "generated_image_id": "UUID引用user_images.id"
--        }
--      ]
--    }
--
-- 下一步：
-- 1. 在 .env 文件中配置 SUPABASE_URL 和 SUPABASE_SERVICE_KEY
-- 2. 确保使用 SERVICE_KEY（不是 ANON_KEY）以绕过 RLS
-- 3. 后端代码中的 storage_service.py 已经兼容此表结构（user_files -> user_images）
