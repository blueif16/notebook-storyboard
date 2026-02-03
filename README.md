# HyperBookLM - AI-Powered Storybook Generator

An AI-powered storybook generation system using LangGraph for agent orchestration and AG-UI protocol for real-time streaming updates.

工作原理：
State 同步：useCoAgent 自动同步后端的 StorybookState，包括 enhanced_story、characters、pages 等

Interrupt 流程：

后端调用 user_interaction 工具触发 interrupt
AG-UI adapter 发送 CustomEvent (name: "on_interrupt")
CopilotKit 捕获事件并调用 useLangGraphInterrupt 的 render 函数
HITLModal 显示对应的审查内容（story_review / character_review / pages_review）
用户批准或提供反馈
调用 resolve 函数将响应返回给后端
后端根据 intention 决定是继续当前阶段还是进入下一阶段
类型驱动的 UI：

type: "story_review" → 显示增强后的故事和角色列表
type: "character_review" → 显示角色肖像网格
type: "pages_review" → 显示故事书页面预览

## 🏗️ V2 Architecture - Hierarchical Subgraphs with Context Isolation

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARENT GRAPH STATE                           │
│  {messages, enhanced_story, characters, pages, storybook_id}   │
│        ↑ Only final outputs, NO accumulated conversations       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ↓                  ↓                  ↓
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  ENHANCE    │   │  PORTRAIT   │   │   STORY     │
│  SUBGRAPH   │   │  SUBGRAPH   │   │  SUBGRAPH   │
├─────────────┤   ├─────────────┤   ├─────────────┤
│ Private:    │   │ Private:    │   │ Private:    │
│  messages   │   │  messages   │   │  messages   │
│             │   │             │   │             │
│ Input:      │   │ Input:      │   │ Input:      │
│  user idea  │   │  enhanced_  │   │  enhanced_  │
│             │   │   story +   │   │   story +   │
│             │   │  characters │   │  characters │
│             │   │             │   │   (images)  │
│             │   │             │   │             │
│ Output:     │   │ Output:     │   │ Output:     │
│  enhanced_  │   │  characters │   │  pages +    │
│   story +   │   │   + images  │   │  storybook  │
│  characters │   │             │   │   _id       │
│             │   │             │   │             │
│ Loop:       │   │ Loop:       │   │ Loop:       │
│  feedback → │   │  feedback → │   │  feedback → │
│   continue  │   │   continue  │   │   continue  │
│  APPROVED → │   │  APPROVED → │   │  APPROVED → │
│   exit      │   │   exit      │   │   exit      │
└─────────────┘   └─────────────┘   └─────────────┘
```

### 🎯 Key Architectural Features (V2)

**Context Isolation**: Each stage operates with **private message context**
- **Enhance** sees only: User story idea
- **Portrait** sees only: Enhanced story + character descriptions
- **Story** sees only: Enhanced story + character images
- **Result**: No context accumulation, cleaner state management

**Subgraph Pattern** (LangGraph Guide Section 6):
- Each stage is a compiled subgraph with internal HITL loop
- Private messages stay in subgraph, don't pollute parent state
- Parent state holds only clean outputs: `enhanced_story`, `characters`, `pages`

**Agent Caching** (LangGraph Guide Section 3.2):
- Agents created once, reused across calls
- Significant performance improvement over recreating agents

**Internal HITL Loops**:
- Each subgraph handles user feedback internally
- Feedback loop: `agent → user_interaction → check response → back to agent or exit`
- Approved: exits subgraph, progresses to next stage
- Escalate: exits to orchestrator for direction change

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```env
# LLM
GOOGLE_API_KEY=your-google-api-key
GEMINI_TEXT_MODEL=gemini-3-flash-preview

# Image Generation
GOOGLE_DEFAULT_MODEL=gemini-3-pro-image-preview

# Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-secret-key

# Server
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3847
```

### 3. Start the Application

**Option A: Using the start script (recommended)**
```bash
./start.sh
```

**Option B: Manual start**
```bash
# Terminal 1: Backend
cd backend
python run_server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3847
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **AG-UI Streaming**: http://localhost:8000/storybook

## 📁 Project Structure (V2)

```
notebook-storyboard/
├── backend/
│   ├── app/
│   │   ├── main.py                    # Unified FastAPI server
│   │   ├── config.py                  # Centralized configuration
│   │   ├── ag_ui/
│   │   │   └── adapter.py             # AG-UI streaming logic
│   │   ├── agents/
│   │   │   └── storybook_agents.py    # 4 agents with caching
│   │   │       • orchestrator (routing)
│   │   │       • enhance (story enhancement)
│   │   │       • portrait (character images)
│   │   │       • story (page generation + save)
│   │   ├── graphs/
│   │   │   ├── storybook_graph.py     # Parent graph + 3 subgraphs
│   │   │   └── routing.py             # Routing logic with logging
│   │   ├── tools/
│   │   │   ├── hitl_tools.py          # user_interaction, escalate, route_to_stage
│   │   │   └── story_tools.py         # Image generation, save tools
│   │   ├── services/
│   │   │   ├── google_image_service.py
│   │   │   └── storage_service.py
│   │   └── routers/
│   │       ├── assets.py
│   │       └── storybooks.py
│   ├── run_server.py                  # Main server launcher
│   └── requirements.txt
│
└── frontend/
    ├── app/
    │   ├── storybook/page.tsx         # Main storybook UI
    │   └── api/copilotkit/route.ts    # CopilotKit integration
    └── components/storybook/          # UI components

```

## 🔧 Key Endpoints

### REST API
- `GET /health` - Health check
- `GET /api/storybooks` - List all storybooks
- `GET /api/storybooks/{id}` - Get specific storybook
- `POST /api/storybooks` - Create storybook (sync)

### AG-UI Streaming
- `POST /storybook` - Generate storybook with real-time streaming updates

## 🎨 Features

### AI-Powered Generation
- **Story Enhancement**: Enriches user prompts with visual details
- **Character Generation**: AI-generated character portraits
- **Page Illustrations**: Custom images for each story page
- **Real-time Streaming**: Live updates via SSE

### Human-in-the-Loop (V2)
- **Enhance stage**: Present enhanced story + characters → feedback loop
- **Portrait stage**: Show character portraits → feedback loop
- **Story stage**: Display pages → feedback loop
- **Escalation**: User can change direction at any stage

### Context Isolation (V2 Key Feature)
```
Before V2: 100+ messages accumulated
[user, ai, tool, ai, user, ai, tool, ai, user, ai, tool...]

After V2: ~5 routing messages only
[user: "story idea", ai: "enhanced", ai: "portraits done", ai: "story complete"]
```

Each stage sees ONLY what it needs:
- Clean handoffs between stages
- No polluted context
- Each subgraph independently testable

## 🏃 Development

### Testing the Backend

```bash
cd backend

# Test graph execution directly
python test_run_storybook.py

# Test HTTP API
python test_http_api.py

# Test Supabase connection
python test_supabase_connection.py
```

### Testing Individual Subgraphs

```python
from app.graphs.storybook_graph import get_enhance_subgraph

# Test enhance alone
enhance = get_enhance_subgraph()
result = await enhance.ainvoke({
    "messages": [{"role": "user", "content": "story about dog"}]
})

# Clean input, clean output, no parent context pollution
```

### Debugging

Enable detailed logging:
```python
# In config.py
DEBUG = True
LANGCHAIN_TRACING_V2 = "true"
```

Check logs for routing decisions:
```
[ROUTE] Evaluating routing from stage: enhance
[ROUTE] user_interaction called with intention=next
[ROUTE] User response: APPROVED
[ROUTE] APPROVED → progressing to portrait
```

## 📚 Technologies

### Backend
- **Framework**: FastAPI
- **Agent Orchestration**: LangGraph (Hierarchical Subgraph Pattern)
- **Streaming Protocol**: AG-UI
- **LLM**: Google Gemini (gemini-3-flash-preview)
- **Image Generation**: Google Gemini (gemini-3-pro-image-preview)
- **Storage**: Supabase

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS, shadcn/ui
- **Agent State**: CopilotKit with AG-UI
- **Real-time Updates**: SSE (Server-Sent Events)

## 🔄 V2 Migration Benefits

### Before (V1)
```python
# Linear workflow, accumulated context
class StorybookState(TypedDict):
    messages: list  # 100+ messages from all stages!
    user_feedback: Optional[str]
```

### After (V2)
```python
# Hierarchical subgraphs, isolated context
class StorybookState(TypedDict):
    messages: list  # Only ~5 routing messages
    enhanced_story: str  # Clean output
    characters: list  # Clean output
    pages: list  # Clean output

# Each subgraph has private messages that stay private
```

**Benefits**:
- ✅ **No context accumulation** - Parent state stays clean
- ✅ **Focused context per stage** - Agents see only what they need
- ✅ **Independently testable** - Each subgraph can be tested alone
- ✅ **Better error isolation** - Errors don't pollute parent state
- ✅ **Agent caching** - Agents created once, reused across calls

## 📖 Documentation

For detailed documentation, see:
- [LangGraph Guide](langgraph_guide) - Comprehensive multi-agent patterns
- [V2 Architecture](HyperBookLM_Architecture_V2.md) - Detailed V2 design doc
- [Backend README](backend/README.md) - Backend-specific docs

## 🐛 Troubleshooting

### AbortError on Frontend
- **Cause**: Backend not running or not accessible
- **Fix**: Ensure backend is running on port 8000

### "run has already errored"
- **Cause**: Normal AG-UI protocol behavior after errors
- **Fix**: Check actual error in RUN_ERROR event

### Import errors
- **Cause**: Virtual environment not activated or missing dependencies
- **Fix**: `source venv/bin/activate` && `pip install -r requirements.txt`

### Subgraph not exiting
- **Check**: Routing logic in `graphs/routing.py`
- **Check**: user_interaction calls have correct `intention` parameter
- **Check**: Tool results are properly extracted

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following V2 patterns
4. Test subgraphs independently
5. Submit a pull request

## 📄 License

See LICENSE file for details.

---

**Powered by LangGraph Hierarchical Subgraphs + AG-UI** 🚀