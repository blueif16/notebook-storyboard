# HyperBookLM Backend

Python FastAPI backend for the HyperBookLM application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
python app/main.py
```

Or use uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── controllers/         # Business logic (Controller layer)
│   │   └── asset_controller.py
│   ├── models/              # Pydantic models (Model layer)
│   │   └── asset.py
│   ├── routers/             # API route handlers (View layer)
│   │   ├── assets.py
│   │   └── storybooks.py
│   ├── services/            # Data access layer
│   │   └── storage.py       # Local JSON file storage
│   └── utils/               # Utility functions
├── data/                    # Local storage directory (gitignored)
│   └── assets.json          # Persisted assets and storybooks
├── tests/                   # Test files
├── config/                  # Configuration files
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## MVC Architecture

The backend follows the Model-View-Controller (MVC) pattern:

- **Models** ([app/models/](app/models/)): Pydantic models for data validation and serialization
- **Views** ([app/routers/](app/routers/)): FastAPI routers that handle HTTP requests/responses
- **Controllers** ([app/controllers/](app/controllers/)): Business logic layer between views and services
- **Services** ([app/services/](app/services/)): Data access layer with local file storage

## API Endpoints

### Assets
- `POST /api/assets/` - Create a new asset
- `GET /api/assets/` - Get all assets
- `GET /api/assets/{asset_id}` - Get asset by ID
- `DELETE /api/assets/{asset_id}` - Delete asset by ID
- `GET /api/assets/type/{asset_type}` - Get assets by type

### Storybooks
- `POST /api/storybooks/` - Create a new storybook
- `GET /api/storybooks/` - Get all storybooks
- `GET /api/storybooks/{storybook_id}` - Get storybook by ID
- `DELETE /api/storybooks/{storybook_id}` - Delete storybook by ID

## Local Storage

Data is persisted to local JSON files in the `data/` directory:
- `data/assets.json` - All assets including storybooks, slides, mindmaps, etc.

The storage is automatically initialized on first run.
