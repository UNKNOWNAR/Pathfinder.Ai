<div align="center">

# 🚀 Pathfinder.Ai

**Intelligent Career Acceleration Platform**

*Real-time job harvesting · AI resume engineering · Voice-enabled mock interviews*

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-42b883?style=flat-square&logo=vue.js)](https://vuejs.org)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Polly%20%7C%20S3-FF9900?style=flat-square&logo=amazonaws)](https://aws.amazon.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

</div>

## ✨ What is Pathfinder.Ai?

Pathfinder.Ai automates the entire student job search lifecycle — from harvesting 7+ live job sources and semantically matching them to a student's skill profile, to rewriting resumes in real-time for specific JDs and running voice-interactive mock interviews powered by AI.

---

## 🏛️ Architecture & AWS Infrastructure

| Service | Component | Role | Monthly Cost |
|---|---|---|---|
| **EC2** | `t3.small` | Gunicorn/Flask API Server | $15.18 |
| **RDS** | `db.t3.micro` | PostgreSQL + pgvector Semantic DB | $12.41 |
| **Bedrock** | Titan Embed v2 | Profile & Job Embeddings | ~$0.00* |
| **Groq API** | Llama 3.3 70B | Interview Q&A, Resume Gen, Ghost Recruiter | Usage-based |
| **Polly** | Neural TTS | Voice synthesis for Ghost Recruiter | $0.60 |
| **S3** | Standard-IA | Resume PDF & Avatar hosting | $0.40 |
| **Lambda** | Python 3.12 | Daily harvest heartbeat trigger | Free Tier |
| **EventBridge** | Scheduler | Cron automation | Free Tier |
| **TOTAL** | | | **~$28.59/mo** |

---

## 🔑 Core Features

### 🔍 Semantic Job Engine
- Harvests **7+ sources** in parallel: LinkedIn (JSearch), Google Jobs, Adzuna, Remotive, Arbeitnow, RemoteOK, WeWorkRemotely
- Filters for fresher/entry-level roles globally
- Generates **pgvector embeddings** (Amazon Titan v2) for every job
- Shows personalized **% match score** per student based on their skill profile embedding

### 📄 AI Resume Engineer
- Rewrites resumes on-the-fly using **Groq Llama 3.3 70B** against a target JD
- Outputs ATS-optimized **LaTeX → PDF** via on-server compilation
- Full **S3-backed versioning**: rename / delete / re-generate

### 🎙️ Ghost Recruiter (Voice Interview)
- Phase-driven conversational interviewer: Introduction → Resume Drilldown → LeetCode → System Design → Behavioral → Wrap-Up
- Reads candidate's profile JSON to ask personalized questions
- Picks questions from a **curated bank** (200+ DSA, 74 System Design, 80+ Behavioral)
- Voice synthesized via **AWS Polly Neural TTS**

### 📊 Interview Coach (Topic-Based)
- Select topic + difficulty → instant questions from curated bank (zero API cost)
- Falls back to Groq LLM for uncovered topics (OOP, Web Development, etc.)
- Per-answer AI evaluation: **score + strengths + improvements + ideal answer**

### ⚡ LeetCode Readiness
- Pulls live stats from LeetCode's public API
- Cross-references company interview question patterns
- Shows topic coverage and recommended practice problems

---

## 🗂️ Project Structure

```
Pathfinder.Ai/
├── backend/
│   ├── api/                  # REST endpoints (auth, jobs, harvest, interview, resume)
│   ├── models/               # SQLAlchemy ORM schemas
│   ├── services/
│   │   ├── harvester.py      # Multi-source parallel job harvester
│   │   ├── rss_sources.py    # RSS/JSON feed fetchers
│   │   ├── embedding.py      # AWS Bedrock Titan v2 embeddings
│   │   ├── interview_service.py  # Question bank + Groq evaluation
│   │   ├── agent_service.py  # Ghost Recruiter stateless AI agent
│   │   ├── llm_service.py    # LaTeX resume generation via Groq
│   │   ├── voice_service.py  # AWS Polly TTS → S3
│   │   └── compiler_service.py   # LaTeX → PDF compilation
│   ├── data/
│   │   └── questions_bank.json   # Curated DSA, System Design & Behavioral bank
│   ├── scripts/
│   │   ├── lambda_harvester.py         # AWS Lambda trigger script
│   │   └── generate_long_lived_token.py # Admin token generator
│   ├── app.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── views/            # JobsView, ProfileView, InterviewView, AdminView...
        ├── components/       # NavBar, shared components
        └── services/api.js   # Centralized Axios config
```

---

## ⚙️ Running Locally

### Prerequisites
- Python 3.12+, Node.js 18+, PostgreSQL with `pgvector` extension
- Copy `backend/.env.example` → `backend/.env` and fill in credentials

### Backend (Flask + Gunicorn)
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py                 # Dev mode
```

### Frontend (Vue.js)
```bash
cd frontend
npm install
npm run serve
```

### Production Sync (Server)
```bash
# On the EC2 instance
bash backend/deploy.sh
```

---

## 🤖 Automation — Daily Harvest Heartbeat

1. Generate a long-lived admin token:
   ```bash
   python backend/scripts/generate_long_lived_token.py
   ```
2. Deploy `backend/scripts/lambda_harvester.py` to AWS Lambda
3. Set `ADMIN_TOKEN` env var in Lambda to the generated token
4. Create an **EventBridge Scheduler** with cron `0 0 * * ? *` targeting the Lambda

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vue.js 3 (Composition API), Neo-Brutalist UI |
| **Backend** | Flask 3, Flask-RESTful, Flask-JWT-Extended, Flask-Limiter |
| **Database** | PostgreSQL 15 + pgvector (semantic search) |
| **AI / LLM** | Groq API (Llama 3.3 70B), AWS Bedrock (Titan Embed v2) |
| **Voice** | AWS Polly Neural TTS |
| **Storage** | AWS S3 (Standard-IA) |
| **Auth** | JWT + Flask-Security-Too |

---

<div align="center">

*Built for Ai for Bharat* 🛥️

</div>
