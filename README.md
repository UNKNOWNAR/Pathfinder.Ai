# Pathfinder.Ai
*(Project documentation and constraints generated to assist Claude & other AI workflows)*

## Description
Pathfinder.Ai is a robust, full-stack application providing an interview preparation, job tracking, and auto-resume tailoring platform. It is built to simulate a "neo-brutalist" theme on the frontend (`Vue.js`) with an API-driven, JWT-secured `Flask` backend managing intelligent interactions via `langchain-huggingface`.

## Directory Layout
- **`backend/`**: Flask REST API — routes in `api/`, ORM schemas in `models/`, business logic in `services/`. Entry point is `backend/app.py`.
- **`frontend/`**: Webpack-bundled `Vue.js 3` Single-Page Application.
- **Dependencies**: `backend/requirements.txt` for Python, `frontend/package.json` for Vue modules.

## Features Accomplished So Far
- **Token-Based Auth System**: Full JWT-backed `Login`, `Signup`, `Logout` flows via `auth_apis.py`, omitting standard form validations in lieu of pure API.
- **Profile Generation Lifecycle**: Complete Create/Read/Update schema and interaction between Vue endpoints (`ProfileView.vue`) and `profile_api.py`.
- **Dynamic Resumes**: Integration with HuggingFace Hub to dynamically create custom resumes and output them into PDF files based on user-entered profile parameters.
- **AWS CI/CD Preparedness**: Initiated GitHub workflows (`.github/`) targeting deployment infrastructures.

## AI Assistant / Developer Workflows
To maintain this repository properly, please refer initially to the following rules:
- Consult `.cursorrules` or `claude.md` prior to executing any code, rewriting logics, or generating boilerplate files.
- Command execution is bound strictly to `E:\WorkSpace\Projects\Electronics Store Q&A System\venv` according to the current host user conventions.
- Frontend package development happens exclusively within `pathfinder-frontend`.

## Starting the Project Locally

### Backend (Flask)
```bash
# Activation of global virtual environment
& "E:\WorkSpace\Projects\Electronics Store Q&A System\venv\Scripts\Activate.ps1"

# Running Backend Server
cd backend
python app.py
```

### Frontend (Vue.js)
```bash
cd frontend
npm run serve
```
