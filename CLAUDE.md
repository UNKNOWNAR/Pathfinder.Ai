Last login: Fri Mar  6 17:42:01 2026 from 13.233.177.4
ubuntu@ip-172-31-42-92:~$ cat /home/ubuntu/error.log | tail -n 20
    mod = importlib.import_module(module)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/ubuntu/Pathfinder.Ai/backend/app.py", line 9, in <module>
    from api import init_routes
  File "/home/ubuntu/Pathfinder.Ai/backend/api/__init__.py", line 2, in <module>
    from api.profile_api import ProfileAPI
  File "/home/ubuntu/Pathfinder.Ai/backend/api/profile_api.py", line 7, in <module>
    from services.s3_service import S3Service
ModuleNotFoundError: No module named 'services.s3_service'
[2026-03-06 21:47:09 +0000] [42676] [INFO] Worker exiting (pid: 42676)# CLAUDE.md

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
HUGGINGFACEHUB_API_TOKEN=...
JSEARCH_API_KEY=...
INTERNSHIPS_API_KEY=...
GOOGLE_JOBS_API_KEY=...
FAANG_WATCH_API_KEY=...
```
`DATABASE_URL` and `HUGGINGFACEHUB_API_TOKEN` are required at startup — the app will raise `ValueError` if either is missing.

---

## Architecture

### Backend (`backend/`)

**Entry point:** `app.py` — creates the Flask app, initializes `db`, `JWTManager`, `Security`, `CORS`, seeds the default admin user, then calls `init_routes(api)`.

**Route registration:** All resources are registered in `api/__init__.py → init_routes()`. To add a new endpoint: create a `Resource` class in `api/`, import it in `api/__init__.py`, and call `api.add_resource(...)` there.

**Services layer:** Business logic lives in `services/`, keeping `api/` handlers thin:
- `llm_service.py` — `LLMService` uses `huggingface_hub.InferenceClient` with `Qwen/Qwen2.5-Coder-7B-Instruct` for LaTeX resume generation
- `compiler_service.py` — `CompilerService` sends LaTeX to TeXLive.net (primary) or YtoTech (fallback) and returns PDF bytes
- `leetcode_client.py` — `LeetCodeClient.fetch_user_data(username)` hits the LeetCode GraphQL API and returns a flat stats dict: `{total_solved, easy_solved, medium_solved, hard_solved, topics{}, contests{}}`
- `embedding.py` — generates pgvector embeddings for student profiles and jobs using `sentence-transformers`
- `utils.py` — shared helpers (e.g. `make_job_hash`)

**Models:** All in `models/`, registered in `models/__init__.py`. Any new model must be imported there so `db.create_all()` picks it up. Key models:
- `User` — roles: `'admin'`, `'company'`, `'student'`; uses Flask-Security password hashing
- `Profile` — student profile, linked to `User` by `user_id`; stores LeetCode username, skills (JSON array), embedding (JSON array, pgvector-ready)
- `Job` + `HarvestLog` — harvested job listings with deduplication via hash
- `Company` — requires admin approval (`is_approved`) before posting jobs
- `CompanyQuestion` — scraped LeetCode questions per company with topics (JSON), difficulty, frequency

**Auth pattern:** All protected routes use `@jwt_required()`. Role checks are done manually via `get_jwt()['role']`. The admin guard `@admin_required` is defined in `api/admin_api.py`.

**API URL prefix:** Most endpoints are bare (`/login`, `/profile`) but newer ones use `/api/` prefix (`/api/jobs`, `/api/leetcode/stats`). Follow the existing prefix for the area you're modifying.

---

### Frontend (`frontend/src/`)

**Router:** `router/index.js` uses `createWebHashHistory` (hash-based URLs). Role-based guards redirect users to their home route on access violations. Student home = `/jobs`, company home = `/company`, admin home = `/admin`.

**API client:** `services/api.js` — Axios instance with `baseURL` from `VUE_APP_API_URL` env var (defaults to `http://127.0.0.1:5000`). JWT token is injected from `localStorage` automatically via a request interceptor.

**Styling:** Neo-brutalist design system. Key CSS variables: `--surface`, `--ink`, `--accent`, `--border`, `--shadow`. The `.box` utility class is used for bordered cards with `box-shadow: 3px 3px 0 var(--ink)`. Do not change the core color scheme or font structure unless explicitly asked.

**View conventions:** Views use Vue 3 `<script setup>` composition API. Data fetching happens in `onMounted`. Error, loading, and empty states are always handled with `v-if/v-else-if/v-else` blocks.

---

## Key Rules

1. **Always read `models/` before modifying `api/`** — schema drives the API contract.
2. **venv is mandatory** — never use system Python; always use `E:\WorkSpace\Projects\Pathfinder.Ai\venv`.
3. **Schema changes require frontend sync** — if a model field changes, update the Vue view that maps that API payload.
4. **No CSRF** — `WTF_CSRF_ENABLED = False` is intentional; do not re-enable it.
8. **PostgreSQL only** — SQLite is not supported anywhere. `DATABASE_URL` must be a `postgresql://` URI.

---

---

## Completed Tasks ✅

### S3 Storage Implementation (Unified Dev/Prod) ✅
1. **AWS S3 Bucket Creation:** Created `pathfinder-uploads-unknownar`.
2. **IAM User Setup:** `pathfinder-backend` configured with `AmazonS3FullAccess`.
3. **S3 Service Class:** Implemented dynamic `boto3` routing to handle public Avatars and private Resumes.
4. **Presigned URLs:** Fixed AWS public access blockages by dynamically generating presigned URLs natively in `profile_api.py`.
5. **Resume History Vault:** Increased maximum resume generations from 2 to 10 and implemented a dedicated UI History section.
6. **LLM Migration:** Successfully migrated Resume Generator from HuggingFace to Groq for faster, highly reliable LaTeX code generation.

### The "Ghost Recruiter" Voice AI Interviewer (AWS Native) ✅
A stateless, event-driven 30-minute AI interviewer powered by **AWS Bedrock (Claude Haiku 4.5)** and **AWS Polly (Matthew Neural)**.

**Architecture:** The AI wakes up only when the user submits an answer. Between answers, 0 tokens are consumed. On refresh, the interview resets.

**6-Phase Interview Flow:**
1. **Introduction:** AI reads user's Profile JSON from DB, greets them by name, asks to explain a project.
2. **Resume Drilldown:** AI probes weaknesses in the project explanation.
3. **LeetCode:** AI picks a coding challenge from `backend/data/questions_bank.json` matching user's skills.
4. **System Design:** AI picks a system design question from the JSON bank.
5. **Behavioral:** AI picks a behavioral question from the JSON bank.
6. **Wrapup:** AI summarizes the interview and gives final feedback.

**Files Created/Modified:**
- `backend/services/agent_service.py` — The Ghost Recruiter brain (picks questions, calls Bedrock, calls Polly).
- `backend/services/voice_service.py` — AWS Polly TTS synthesis, uploads MP3 to S3.
- `backend/services/llm_service.py` — Upgraded to Claude Haiku 4.5 (`anthropic.claude-haiku-4-5-20251001-v1:0`).
- `backend/services/interview_service.py` — Upgraded to Claude Haiku 4.5.
- `backend/data/questions_bank.json` — Placeholder question bank (user will replace with curated data).
- `backend/api/interview_api.py` — Added `GhostInterviewStep` endpoint at `/api/interview/ghost_step`.
- `frontend/src/views/InterviewView.vue` — Full Ghost Interview UI with phase indicator, evaluation display, audio playback.

### Smart Semantic Job Matching (pgvector) ✅ Complete
The database correctly stores `pgvector` embeddings natively or uses a Python numpy cosine-similarity fallback.

### TODO: Replace Question Bank
The user will provide curated LeetCode, System Design, and Behavioral questions in JSON format to replace the placeholder `backend/data/questions_bank.json`.

