# 🤖 Agent Architecture Quick Reference

**Pure agent autonomy. Maximum flexibility. Minimal structure.**

---

## 🎯 Core Philosophy

**Everything flows through natural conversation.** No predetermined fields, modes, or routing logic. Agents decide when to ask for approval, when to show assets, when to generate.

---

## 🏗️ Architecture Overview

```
User Chat
    ↓
Orchestrator Agent
    ├─→ enhance_and_extract(story_text)
    ├─→ generate_character_portrait(desc) × N
    ├─→ request_user_input() [optional HITL]
    └─→ Delegates to Story Generator
            ↓
Story Generator Agent
    ├─→ generate_page_image(prompt, refs, page_num) × N
    │   └─→ Calls google_image_to_image(prompt, [char_ids, prev_page])
    └─→ save_storybook(title, desc, pages)
            ↓
Complete storybook saved to DB
```

---

## 🛠️ Tools (5 Total)

| Tool | Owner | Purpose |
|------|-------|---------|
| `enhance_and_extract` | Orchestrator | Story enhancement + character extraction |
| `generate_character_portrait` | Orchestrator | Create character images |
| `request_user_input` | Both | HITL interrupts (optional) |
| `generate_page_image` | Story Generator | Create page illustrations with references |
| `save_storybook` | Story Generator | Bundle and save to DB |

---

## 📊 State Flow

```python
class StorybookState(TypedDict):
    messages: Annotated[list, add_messages]  # Conversation history
    
    # Derived from tool results (for AG-UI display)
    characters: list[dict]  # [{name, image_id, image_url}]
    pages: list[dict]       # [{page_number, image_id, image_url}]
    stage: str              # Current pipeline stage
    progress: float         # 0-100
    storybook_id: str       # Final saved ID
```

**No complex routing.** Just messages flowing between agents + tools auto-populating state.

---

## 💬 Conversation Examples

### Auto-Generate (No Interrupts)

```
User: "Create a magical story about a brave mouse"

Orchestrator:
  ├─ enhance_and_extract()
  ├─ generate_character_portrait() × 3
  └─ Delegates: "Story ready. Characters: Luna (id: abc), Max (id: def)..."

Story Generator:
  ├─ Page 1: generate_page_image("Luna in meadow", [abc])
  ├─ Page 2: generate_page_image("Luna explores", [abc, page_1_id])
  ├─ ... × 8 pages
  └─ save_storybook("The Brave Mouse", desc, pages)

→ Complete! 8 pages, 3 characters
```

### With Approval (HITL)

```
User: "Create a story, show me characters first"

Orchestrator:
  ├─ enhance_and_extract()
  ├─ generate_character_portrait() × 3
  └─ request_user_input("Characters ready. Approve?", images=[...])
      ← INTERRUPT
      
User: "The mouse looks too serious, make him playful"

Orchestrator resumes:
  ├─ generate_character_portrait("playful mouse...")
  ├─ request_user_input("Better?", images=[new_mouse])
      ← INTERRUPT
      
User: "Perfect!"

Orchestrator:
  └─ Delegates with approved characters

Story Generator:
  └─ ... generates pages ...
```

---

## 🔧 Key Implementation Details

### Reference Image Logic

**How it works:**
```python
# Story Generator agent decides:
references = []
references.append(luna_character_id)  # Character in this scene
references.append(previous_page_id)   # Same forest setting

# Tool call:
result = await generate_page_image(
    prompt="Luna discovers magic book in forest",
    reference_image_ids=references,
    page_number=3
)

# Internally calls:
google_image_to_image(
    prompt=enhanced_prompt,
    image_asset_ids=references  # Max 14 IDs
)
```

**Agent decides when to reference:**
- Character appears → use character ID
- Same setting → use previous page ID
- New setting → only character IDs
- No rules, pure judgment

### Database Schema

**Table: `storybooks`**
```sql
CREATE TABLE storybooks (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  pages JSONB NOT NULL,  -- [{page_number, image_id, image_url, plot}]
  page_count INTEGER,
  created_at TIMESTAMPTZ
);
```

**Table: `user_images`** (existing)
- Stores all generated images
- Referenced by `image_id` in storybook pages and characters

---

## 🚀 Running the System

### Development Mode:

```bash
# Terminal 1: AG-UI Backend
cd backend
python -m app.ag_ui.server

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: `http://localhost:3847/storybook`

### Test with curl:

```bash
curl -X POST http://127.0.0.1:8001/storybook \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Create a whimsical story about a cat"}],
    "thread_id": "test-123",
    "run_id": "run-456"
  }'
```

Should stream AG-UI events (SSE format).

---

## 📚 Code Locations

| Component | File Path |
|-----------|-----------|
| **Tools** | `backend/app/tools/story_tools.py` |
| **Agents** | `backend/app/agents/storybook_agents.py` |
| **Graph** | `backend/app/graphs/storybook_graph.py` |
| **AG-UI Adapter** | `backend/app/ag_ui/adapter.py` |
| **AG-UI Server** | `backend/app/ag_ui/server.py` |
| **Image Services** | `backend/app/services/google_image_service.py` |
| **Frontend Page** | `frontend/app/storybook/page.tsx` |
| **CopilotKit Route** | `frontend/app/api/copilotkit/route.ts` |
| **Components** | `frontend/components/storybook/` |
| **State Types** | `frontend/types/storybook-state.ts` |

---

## 🔍 Troubleshooting

**"Table 'storybooks' doesn't exist"**
- Run migration: `backend/database/migrations/002_storybooks_table.sql`

**"Module not found: @copilotkit/react-core"**
- Run: `cd frontend && npm install`

**"CORS error" in browser**
- Check AG-UI server is running on port 8001
- Check `server.py` has `http://localhost:3847` in CORS origins

**"No events streaming"**
- Check browser Network tab for SSE connection to `/api/copilotkit`
- Check AG-UI backend logs for errors
- Verify HttpAgent URL matches backend endpoint

**"Characters not showing in chat"**
- Check `useCoAgentStateRender` is rendering CharacterGrid
- Check backend is emitting `STATE_DELTA` events
- Open React DevTools to inspect state

---

## 🎨 Customization

### Change Agent Behavior:

Edit prompts in `backend/app/agents/storybook_agents.py`:

```python
# Make orchestrator always show characters:
prompt = """...
3. ALWAYS show characters to user with request_user_input()
..."""

# Make story generator create more pages:
prompt = """...
2. Decide page count: 10-15 pages (unless user specified)
..."""
```

### Change UI Appearance:

Edit components in `frontend/components/storybook/`:
- `CharacterGrid.tsx` - Character card styling
- `PageGrid.tsx` - Page thumbnail layout
- `ProgressIndicator.tsx` - Progress bar colors/icons

### Add New Tools:

```python
# In backend/app/tools/story_tools.py
@tool
async def regenerate_character(character_name: str, new_description: str):
    """Regenerate a specific character with new traits."""
    # Implementation...
```

Add to appropriate agent's tool list in `agents/storybook_agents.py`.

---

**Everything is ready. Just run the migration and install dependencies!**
