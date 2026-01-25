-- ============================================
-- Migration 002: Create storybooks table
-- ============================================
-- Purpose: Support agent-based save_storybook tool
-- Run in Supabase SQL Editor after 01_initial_setup.sql

-- Create storybooks table (for agent-generated storybooks)
CREATE TABLE IF NOT EXISTS public.storybooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  pages JSONB NOT NULL,  -- Array of {page_number, image_id, image_url, plot?}
  page_count INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_storybooks_created_at 
ON public.storybooks(created_at DESC);

-- Enable RLS
ALTER TABLE public.storybooks ENABLE ROW LEVEL SECURITY;

-- Service role can manage all storybooks (for agents)
CREATE POLICY "Service role can manage all storybooks"
ON public.storybooks FOR ALL
TO service_role
USING (true);

-- Public read access for viewing
CREATE POLICY "Anyone can view storybooks"
ON public.storybooks FOR SELECT
TO anon, authenticated
USING (true);

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_storybooks_updated_at
BEFORE UPDATE ON public.storybooks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Notes
-- ============================================
-- This table is separate from user_storybooks:
-- - storybooks: Agent-generated via save_storybook tool (simpler schema)
-- - user_storybooks: Legacy/manual storybooks with user_id and source tracking
--
-- Both can coexist. Frontend can merge results from both tables if needed.
-- ============================================
