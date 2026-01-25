# Agent-Based Storybook

Pure agent autonomy. Conversation-driven. Zero fixed sequences.

## Setup

```bash
cd backend
pip install -r requirements.txt

# Run migration in Supabase SQL Editor:
# CREATE TABLE IF NOT EXISTS storybooks (
#   id UUID PRIMARY KEY,
#   title TEXT NOT NULL,
#   description TEXT,
#   pages JSONB NOT NULL DEFAULT '[]'::jsonb,
#   page_count INTEGER DEFAULT 0,
#   created_at TIMESTAMPTZ DEFAULT NOW()
# );
```

## Test

```bash
# Basic tests (no API calls)
python test_agents.py

# Full test (costs credits - generates real images)
python test_agents.py --full
```

## Run

```bash
# AG-UI server
cd app
python -m ag_ui.server
# Runs on port 8001

# Or regular FastAPI
uvicorn app.main:app --reload
# Runs on port 8000
```

## API

### New Agent Endpoint (Unified)
```bash
POST /storybooks/agent-generate
{
  "story_text": "Luna is a brave mouse...",
  "style": "whimsical",
  "page_count": 8
}
```

### Old Endpoints (Still Work)
```bash
POST /storybooks/generate-characters  # Phase 1
POST /storybooks/generate-story        # Phase 2
```

## Architecture

```
app/
├── tools/story_tools.py      # 5 tools
├── agents/storybook_agents.py # 2 agents
├── graphs/storybook_graph.py  # Linear graph
└── ag_ui/                     # Streaming
    ├── adapter.py
    └── server.py
```

**Flow:** orchestrator (enhance + characters) → story_generator (pages + save) → done

**Tools:**
1. enhance_and_extract - Story + characters
2. generate_character_portrait - Character image
3. generate_page_image - Page with references
4. save_storybook - Persist to DB
5. request_user_input - HITL interrupt

**Agents decide everything:** page count, references, when to interrupt. Pure judgment, zero rules.
