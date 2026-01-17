# Environment Configuration Guide

## Overview

This project uses a centralized `.env` file at the project root for API keys and essential configuration. Optional service-specific settings can be configured in their respective folders.

## Quick Start

1. Copy the root `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   - `OPENAI_API_KEY` - Required for LLM features
   - `GEMINI_API_KEY` - Required for image and video generation
   - `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` - Required if using cloud storage
   - Other API keys as needed

3. (Optional) Customize service-specific settings:
   - Backend: Copy `backend/config.example.env` to `backend/.env.local`
   - Frontend: Copy `frontend/config.example.env` to `frontend/.env.local`

## File Structure

```
mynotebook/
├── .env                          # Main config (API keys) - CREATE THIS
├── .env.example                  # Template for main config
├── backend/
│   ├── config.example.env        # Optional backend-specific settings
│   └── .env.local               # (Optional) Your backend overrides
└── frontend/
    ├── config.example.env        # Optional frontend-specific settings
    └── .env.local               # (Optional) Your frontend overrides
```

## Configuration Priority

Both frontend and backend load environment variables in this order:

1. **Root `.env`** - Main configuration (API keys, essential settings)
2. **Local overrides** - Service-specific `.env.local` files (optional)

## Required API Keys

### Essential
- `OPENAI_API_KEY` - For LLM features and storybook generation
- `GEMINI_API_KEY` - For image generation and Veo video

### Optional (based on features used)
- `FAL_API_KEY` - Alternative image generation service
- `ELEVENLABS_API_KEY` - Audio/voice generation
- `HYPERBROWSER_API_KEY` - Web scraping features
- `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` - Cloud storage (or use local storage)

## Service-Specific Settings

### Backend (`backend/config.example.env`)
- Image generation defaults (model, resolution, aspect ratio)
- Video generation defaults (FPS, frames, resolution)
- Storage configuration (local directory, user ID)
- FFmpeg path

### Frontend (`frontend/config.example.env`)
- Model selection (summary model, Gemini model, Veo model)
- API URL for development

## Security Notes

- **Never commit `.env` files** - They contain secrets
- Keep `.env.example` files updated but without real values
- Use `.env.local` for personal overrides (also gitignored)
- Rotate API keys regularly

## Troubleshooting

### Backend can't find API keys
- Ensure `.env` exists in the project root (`/home/ran/favprojects/mynotebook/.env`)
- Check that the file has proper permissions
- Verify API keys are set without quotes: `OPENAI_API_KEY=sk-...`

### Frontend can't access environment variables
- Restart the Next.js dev server after changing `.env`
- Public variables must be prefixed with `NEXT_PUBLIC_`
- Server-side variables don't need the prefix

### Changes not taking effect
- Restart both frontend and backend servers
- Clear Next.js cache: `rm -rf frontend/.next`
- Verify the `.env` file is in the correct location
