<div align="center">

# 🚀 Pathfinder.Ai (Serverless Edition)

**Intelligent Career Acceleration Platform — Zero-Cost Architecture**

*Real-time job harvesting · AI resume engineering · Voice-enabled mock interviews*

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-42b883?style=flat-square&logo=vue.js)](https://vuejs.org)
[![Render](https://img.shields.io/badge/Render-Live-00cf91?style=flat-square&logo=render)](https://render.com)
[![Neon](https://img.shields.io/badge/Neon-PostgreSQL-00e599?style=flat-square&logo=neon)](https://neon.tech)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

</div>

## ✨ What is Pathfinder.Ai?

Pathfinder.Ai automates the entire student job search lifecycle. This **Serverless Edition** is a specialized migration designed to run entirely on high-performance free tiers, removing over $30/month in infrastructure costs while maintaining the same powerful AI features.

---

## 🏛️ Zero-Cost Cloud Architecture

We have migrated from traditional AWS infrastructure to a modern, serverless stack that costs **$0.00/month**.

| Service | Technology | Role | Cost |
|---|---|---|---|
| **Frontend** | **GitHub Pages** | Static Web Hosting | $0.00 |
| **Backend** | **Render (Free Tier)** | Python/Flask API Server | $0.00 |
| **Database** | **Neon.tech** | Serverless PostgreSQL + pgvector | $0.00 |
| **Embeddings**| **Jina AI** | Semantic Skill & Job Matching | $0.00* |
| **LLM (AI)** | **Groq API** | Llama 3.3 70B (Resume & Interviews) | $0.00* |
| **Storage** | **Supabase Storage**| Resume PDFs & User Avatars | $0.00 |
| **Cron Jobs** | **GitHub Actions** | Daily Harvester Heartbeat | $0.00 |
| **Voice** | **Web Speech API** | On-device Neural TTS synthesis | $0.00 |
| **TOTAL** | | | **$0.00/mo** |

*\*Within free tier limits (1M tokens/month).*

---

## 🔑 Core Features

### 🔍 Semantic Job Engine
- Harvests **7+ sources** in parallel: LinkedIn (JSearch), Google Jobs, Adzuna, Remotive, Arbeitnow, RemoteOK, WeWorkRemotely.
- Powered by **Jina AI Embeddings** (v3) for high-precision semantic matching between resumes and JDs.
- Real-time **% match score** calculations inside the database using `pgvector`.

### 📄 AI Resume Engineer
- Generates ATS-optimized resumes using **Groq Llama 3.3 70B**.
- Real-time **LaTeX → PDF** compilation via the TeXLive.net API.
- Full version history and cloud storage backed by **Supabase**.

### 🎙️ Ghost Recruiter (Voice Interview)
- Interactive conversational interviewer with 5 phases: Intro → Resume → DSA → System Design → Behavioral.
- **Low-latency Voice**: Replaced AWS Polly with high-performance browser-native Web Speech synthesis.
- Curated bank of **350+ technical questions** for zero-cost fallback logic.

### ⚡ Automation — Daily Harvest
- No manual triggers needed. **GitHub Actions** runs a cron job every 24 hours.
- Uses a persistent **System API Key** to securely trigger the multi-source harvester on Render.

---

## 🗂️ Project Structure

```
Pathfinder.Ai/
├── backend/
│   ├── api/                  # REST endpoints (auth, jobs, harvest, interview, resume)
│   ├── models/               # SQLAlchemy ORM (Neon PostgreSQL)
│   ├── services/
│   │   ├── harvester.py      # Multi-source parallel job harvester
│   │   ├── embedding.py      # Jina AI Cloud Embeddings
│   │   ├── s3_service.py     # Supabase Storage Wrapper
│   │   ├── llm_service.py    # Groq Llama 3.3 Integration
│   │   └── compiler_service.py   # LaTeX → PDF (Remote Compilation)
│   ├── app.py
│   └── requirements.txt
├── frontend/                 # Vue.js 3 Neo-Brutalist UI
└── .github/workflows/        # Automation (Deploy & Cron)
```

---

## ⚙️ Deployment & Setup

### Backend (Render)
1. Set `PYTHON_VERSION` environment variable to `3.11.9`.
2. Connect your repository and use `pip install -r requirements.txt`.
3. Set all API keys (Groq, Jina, Neon, Supabase, SYSTEM_API_KEY) in the dashboard.

### Frontend (GitHub Pages)
1. Add `RENDER_BACKEND_URL` and `SYSTEM_API_KEY` to your GitHub Repository Secrets.
2. The GitHub Action will automatically build the Vue app and inject the URL.

---

<div align="center">

*Engineered for speed, built for zero cost.* ⛵

</div>
