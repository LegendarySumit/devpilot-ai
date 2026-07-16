# DevPilot AI

Build • Debug • Document

## Locked Tech Stack

- Frontend: React (Vite), TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Deployment: Vercel (Frontend), Render (Backend), Neon PostgreSQL (Database)

## Platform Constraints

- No Docker
- No Redis
- No Microservices

## Repository Structure

- frontend/
- backend/
- docs/
- .gitignore
- README.md
- LICENSE

## Phase 0 Scope

Only the Home workspace foundation is implemented now:

- Navbar
- WorkspaceInput
- QuickActions

## Product Architecture Direction

- Workspace-first experience instead of separate feature pages
- Unified artifact intake routed by ClassifierService
- Pipeline execution via PromptPipeline, DebugPipeline, and DocumentPipeline
- Unified timeline foundation via WorkspaceItem model

## Run Frontend

1. cd frontend
2. npm install
3. npm run dev

## Run Backend

1. cd backend
2. python -m venv .venv
3. .venv\\Scripts\\activate
4. pip install -r requirements.txt
5. uvicorn app.main:app --reload
