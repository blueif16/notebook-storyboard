-- ============================================
-- Migration 003: Create style_catalog table
-- ============================================
-- Purpose: Pre-baked illustration style options with sample images
-- for the style selection stage. Agent picks keys, frontend
-- renders cards with name + description + sample image.
-- Run in Supabase SQL Editor after 002_storybooks_table.sql

-- Create style_catalog table
CREATE TABLE IF NOT EXISTS public.style_catalog (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key TEXT UNIQUE NOT NULL,            -- e.g. "watercolor", "cartoon", "anime"
  name TEXT NOT NULL,                  -- Display name: "Watercolor"
  description TEXT NOT NULL,           -- Full style prompt used downstream
  image_url TEXT,                      -- Sample image URL (Supabase storage)
  sort_order INTEGER DEFAULT 0,        -- Display ordering
  active BOOLEAN DEFAULT true,         -- Soft-delete / hide without removing
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for key lookups (agent sends keys)
CREATE INDEX IF NOT EXISTS idx_style_catalog_key
ON public.style_catalog(key);

-- Index for listing active styles in order
CREATE INDEX IF NOT EXISTS idx_style_catalog_active_sort
ON public.style_catalog(active, sort_order);

-- Enable RLS
ALTER TABLE public.style_catalog ENABLE ROW LEVEL SECURITY;

-- Service role can manage catalog
CREATE POLICY "Service role can manage style_catalog"
ON public.style_catalog FOR ALL
TO service_role
USING (true);

-- Public read access (frontend + agents need to read)
CREATE POLICY "Anyone can view style_catalog"
ON public.style_catalog FOR SELECT
TO anon, authenticated
USING (true);

-- Auto-update updated_at
CREATE TRIGGER update_style_catalog_updated_at
BEFORE UPDATE ON public.style_catalog
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
