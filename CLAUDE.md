# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
# Run the Flask dev server (always use the project venv — MANDATORY)
E:\WorkSpace\Projects\Pathfinder.Ai\venv\Scripts\python.exe backend/app.py

# Install/update dependencies
E:\WorkSpace\Projects\Pathfinder.Ai\venv\Scripts\pip.exe install -r backend/requirements.txt
```

### Frontend
All frontend commands must be run from inside the `frontend/` directory:
```bash
cd frontend
npm run serve   # dev server (proxies API to localhost:5000)
npm run build   # production build
npm run lint    # ESLint via vue-cli-service
```

### Required `.env` file
Place at `backend/.env` (loaded automatically by `config.py` via `python-dotenv`):
```
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
SECRET_KEY=...
SECURITY_PASSWORD_SALT=...
BEDROCK_API_KEY=...
GROQ_API_KEY=...
JSEARCH_API_KEY=...
INTERNSHIPS_API_KEY=...
GOOGLE_JOBS_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-south-1
AWS_S3_BUCKET_NAME=...
```
`DATABASE_URL` and `BEDROCK_API_KEY` are required at startup.

---

## Architecture

### Backend (`backend/`)

**Entry point:** `app.py` — creates the Flask app, initializes `db`, `JWTManager`, `Security`, `CORS`, seeds the default admin user, then calls `init_routes(api)`.

**Route registration:** All resources are registered in `api/__init__.py → init_routes()`.

**Services layer:** Business logic lives in `services/`, keeping `api/` handlers thin:
- `llm_service.py` — `LLMService` uses Bedrock (Qwen 3 Next 80B) with a Groq (Llama 3.3 70B) fallback for LaTeX resume generation.
- `compiler_service.py` — `CompilerService` sends LaTeX to TeXLive.net (primary) or YtoTech (fallback) and returns PDF bytes.
- `agent_service.py` — The "Ghost Recruiter" agent for AI interviews using Bedrock and Polly.
- `embedding.py` — generates pgvector embeddings using Amazon Titan Embeddings v2.
- `harvester.py` — Unified engine for 7 job sources (LinkedIn, Internships, GoogleJobs, Remotive, Arbeitnow, RemoteOK, WeWorkRemotely).

**Models:** All in `models/`, registered in `models/__init__.py`.
- `User` — roles: `'admin'`, `'company'`, `'student'`.
- `Profile` — student profile, stores skills, and pgvector embeddings.
- `Job` + `HarvestLog` — harvested job listings with SHA-256 deduplication.

**Auth pattern:** All protected routes use `@jwt_required()`. Admin guard `@admin_required` is in `api/admin_api.py`.

---

### Frontend (`frontend/src/`)

**Router:** `router/index.js` handles role-based guards and routing.
**API client:** `services/api.js` — Axios instance with JWT injection and neo-brutalist error handling.
**Styling:** Neo-brutalist design system using high-contrast borders and shadows.

---

## Key Rules

1. **Always read `models/` before modifying `api/`**.
2. **venv is mandatory** — use `E:\WorkSpace\Projects\Pathfinder.Ai\venv`.
3. **No CSRF** — `WTF_CSRF_ENABLED = False` is intentional.
4. **PostgreSQL only** — `DATABASE_URL` must be a `postgresql://` URI.

---

## Completed Tasks ✅

### S3 Storage Implementation ✅
Implemented public Avatars and private Resumes storage via `S3Service` with presigned URLs.

### The "Ghost Recruiter" Voice AI Interviewer ✅
A stateless AI interviewer powered by **AWS Bedrock (Qwen 3 Next 80B)** and **AWS Polly**. Supports 6-phase flow from Intro to Wrapup.

### Smart Semantic Job Matching ✅
Native `pgvector` search with Python cosine-similarity fallback for career pathfinding.

### Advanced Job Harvesting Engine ✅
Unified engine for 7 production-ready sources with live logging and quota tracking in the Admin Dashboard.

### Bedrock-First AI Strategy ✅
Standardized across Resume Generation and Ghost Recruiter using `qwen.qwen3-next-80b-a3b` with high-speed fallback to Groq.

### Codebase Purge ✅
Successfully removed all legacy references to "FaangWatch" and "Adzuna".

### TODO: Replace Question Bank
The user will provide curated LeetCode, System Design, and Behavioral questions in JSON format to replace the placeholder `backend/data/questions_bank.json`.
