from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'default-dev-password-salt')

    # ── Database (Neon.tech PostgreSQL) ──────────────────────────────────────
    _db_url = os.getenv('DATABASE_URL')
    if not _db_url:
        raise ValueError("CRITICAL: DATABASE_URL is missing!")
    # Fix legacy 'postgres://' prefix for SQLAlchemy 1.4+
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # ── Auth ──────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    WTF_CSRF_ENABLED = False
    SECURITY_WTF_CSRF_ENABLED = False
    SECURITY_URL_PREFIX = '/security'

    # ── AI / LLM (Groq) ───────────────────────────────────────────────────────
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

    # ── Embeddings (Jina AI) ──────────────────────────────────────────────────
    JINA_API_KEY = os.getenv('JINA_API_KEY', '')

    # ── Job Harvesting APIs ───────────────────────────────────────────────────
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    JSEARCH_API_KEY = RAPIDAPI_KEY
    INTERNSHIPS_API_KEY = RAPIDAPI_KEY
    GOOGLE_JOBS_API_KEY = RAPIDAPI_KEY

    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '')
    ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY', '')

    # ── File Storage (Supabase) ───────────────────────────────────────────────
    _raw_url = os.getenv('SUPABASE_URL', '')
    _raw_key = os.getenv('SUPABASE_SERVICE_KEY', '')
    SUPABASE_URL = _raw_url.strip().strip("'").strip('"')
    if SUPABASE_URL.endswith('/'):
        SUPABASE_URL = SUPABASE_URL[:-1]
    SUPABASE_SERVICE_KEY = _raw_key.strip().strip("'").strip('"')
