-- ============================================
-- Migration: [描述这个迁移的目的]
-- Created: [YYYY-MM-DD]
-- Author: [作者名]
-- ============================================

-- ============================================
-- UP Migration (应用更改)
-- ============================================

-- 在这里编写你的数据库更改
-- 例如：
-- CREATE TABLE IF NOT EXISTS public.new_table (
--   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--   name TEXT NOT NULL,
--   created_at TIMESTAMPTZ DEFAULT NOW()
-- );

-- CREATE INDEX IF NOT EXISTS idx_new_table_name ON public.new_table(name);

-- ============================================
-- DOWN Migration (回滚更改) - 可选
-- ============================================

-- 如果需要回滚，取消注释并编写回滚逻辑
-- DROP TABLE IF EXISTS public.new_table;

-- ============================================
-- 验证
-- ============================================

-- 在这里添加验证查询，确保迁移成功
-- SELECT COUNT(*) FROM public.new_table;
