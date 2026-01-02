# HyperBookLM - My Notebook

A powerful notebook application with AI-powered content generation, featuring storybooks, slides, mindmaps, and more.

## Project Structure

```
mynotebook/
├── frontend/          # Next.js frontend application
│   ├── app/
│   │   ├── page.tsx                    # Main application page
│   │   ├── library/
│   │   │   ├── page.tsx                # Asset library page
│   │   │   └── storybook/
│   │   │       └── [id]/
│   │   │           └── page.tsx        # Individual storybook viewer
│   │   └── api/                        # API routes
│   │       ├── gemini/
│   │       │   ├── storybook/          # Storybook generation API
│   │       │   └── slides/             # Slides generation API
│   │       ├── gpt/
│   │       │   └── mindmap/            # Mindmap generation API
│   │       ├── chat/                   # Chat API
│   │       ├── audio/                  # Audio generation API
│   │       └── scrape/                 # Web scraping API
│   ├── components/
│   │   ├── Navbar.tsx                  # Navigation bar with library icon
│   │   ├── StoryBook.tsx               # Interactive storybook component
│   │   ├── OutputsPanel.tsx            # Outputs display panel
│   │   ├── SourcesPanel.tsx            # Sources management
│   │   ├── ChatInterface.tsx           # Chat interface
│   │   └── MindMap.tsx                 # Mindmap visualization
│   └── lib/
│       ├── storage.ts                  # LocalStorage utilities
│       ├── types.ts                    # TypeScript type definitions
│       └── utils.ts                    # Utility functions
│
└── backend/           # Python FastAPI backend
    ├── app/
    │   ├── main.py                     # FastAPI entry point
    │   ├── routers/                    # API route handlers
    │   ├── models/                     # Pydantic models
    │   ├── services/                   # Business logic
    │   └── utils/                      # Utility functions
    └── tests/                          # Test files
```

## Features

### 🎨 Interactive Storybook
- Beautiful page-flip animations using Framer Motion
- Two-page spread layout like a real book
- Auto-save to localStorage for persistence
- Export as JSON for backup

### 📚 Asset Library
- Centralized repository for all generated content
- Filter by type: Storybooks, Slides, Mindmaps, Audio, Summaries
- Quick actions: View, Export, Delete
- Metadata tracking: creation date, source count

### 🔄 Auto-Save System
- All generated storybooks automatically saved to localStorage
- Long-lived storage across browser sessions
- Smart title generation from source materials
- Metadata preservation

### 🎯 Navigation
- Library icon in navbar for quick access
- Breadcrumb navigation
- Responsive design for mobile and desktop

## Getting Started

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

The backend API will be available at `http://localhost:8000`

## Environment Variables

### Frontend (.env.local)
```
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
HYPERBROWSER_API_KEY=your_hyperbrowser_api_key
```

### Backend (.env)
```
# Add backend-specific environment variables here
```

## Usage

1. **Add Sources**: Upload PDFs or add URLs to scrape content
2. **Analyze**: Click "Analyze Sources" to generate all outputs
3. **View Storybook**: Check the Outputs panel for your generated storybook
4. **Access Library**: Click the Library icon in the navbar to view all saved assets
5. **Export**: Download storybooks as JSON for backup or sharing

## Storage

All generated assets are stored in the browser's localStorage:
- Key: `hyperbooklm_assets`
- Format: JSON array of StoredAsset objects
- Persistence: Survives browser restarts
- Capacity: ~5-10MB depending on browser

## API Endpoints

### Frontend API Routes
- `POST /api/gemini/storybook` - Generate storybook from sources
- `POST /api/gemini/slides` - Generate presentation slides
- `POST /api/gpt/mindmap` - Generate mindmap
- `POST /api/chat` - Chat with AI about sources
- `POST /api/audio` - Generate audio overview
- `POST /api/scrape` - Scrape web content
- `POST /api/upload` - Upload and process PDFs

### Backend API
See backend documentation for Python FastAPI endpoints.

## Technologies

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS, shadcn/ui
- **Animations**: Framer Motion
- **State**: React Hooks
- **Storage**: LocalStorage API
- **AI**: Google Gemini, OpenAI GPT

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.x
- **API Docs**: Swagger UI, ReDoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions:
- Frontend: Check browser console for errors
- Backend: Check FastAPI logs
- Storage: Clear localStorage if experiencing issues

---

**Powered by Hyperbrowser** 🚀
# notebook-storyboard
