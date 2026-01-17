# Documentation Index

Welcome to the HyperBookLM documentation. This folder contains organized documentation for all aspects of the project.

## 📁 Documentation Structure

### [setup/](setup/)
Configuration and environment setup guides
- [CONFIGURATION.md](setup/CONFIGURATION.md) - Environment configuration guide for API keys and settings

### [database/](database/)
Database and storage documentation
- [SUPABASE_MIGRATION.md](database/SUPABASE_MIGRATION.md) - Guide for migrating to new Supabase API keys
- [supa_connection.md](database/supa_connection.md) - Supabase connection and API key documentation

### [libraries/](libraries/)
Third-party libraries and integrations
- [instructor.md](libraries/instructor.md) - Instructor library documentation for structured LLM outputs

### [backend/](backend/)
Backend-specific documentation (Python/FastAPI)
- Coming soon: API endpoints, services, and backend architecture

### [frontend/](frontend/)
Frontend-specific documentation (Next.js/React)
- Coming soon: Components, pages, and frontend architecture

### [architecture/](architecture/)
System architecture and design documents
- Coming soon: Overall system design, data flow, and architectural decisions

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS, shadcn/ui
- **Animations**: Framer Motion
- **State Management**: React Hooks
- **AI SDKs**:
  - OpenAI SDK
  - Google Gemini SDK
  - Anthropic SDK
  - Hyperbrowser SDK

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.x
- **Validation**: Pydantic
- **HTTP Client**: httpx
- **AI Integration**: Google Generative AI

### Database & Storage
- **Cloud Storage**: Supabase
- **Local Storage**: Browser LocalStorage API

### Development Tools
- **Package Manager**: npm (frontend), pip (backend)
- **Type Checking**: TypeScript (frontend), Pydantic (backend)
- **Testing**: pytest (backend)
- **Linting**: ESLint (frontend)

## 🚀 Quick Links

- [Main README](../README.md) - Project overview and getting started
- [Setup Guide](setup/CONFIGURATION.md) - Environment configuration
- [Supabase Migration](database/SUPABASE_MIGRATION.md) - Database setup

## 📝 Contributing to Documentation

When adding new documentation:
1. Place files in the appropriate category folder
2. Update this README.md with links to new documents
3. Use clear, descriptive filenames
4. Follow markdown best practices
5. Include code examples where applicable
