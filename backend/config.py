from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'default-dev-password-salt')

    # Database Configuration: Strict PostgreSQL Requirement
    _db_url = os.getenv('DATABASE_URL')
    
    if not _db_url:
        raise ValueError("CRITICAL: DATABASE_URL is missing! PostgreSQL is strictly required across all environments.")
        
    # Heroku/AWS sometimes returns 'postgres://' which SQLAlchemy 1.4+ requires as 'postgresql://'
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Disable CSRF — this is a REST API using token-based auth, not forms
    WTF_CSRF_ENABLED = False
    SECURITY_WTF_CSRF_ENABLED = False

    # Move Flask-Security's built-in routes away from /login so our API can use it
    SECURITY_URL_PREFIX = '/security'

    # RapidAPI Key — Used for LinkedIn, Internships, and Google Jobs
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    JSEARCH_API_KEY = RAPIDAPI_KEY
    INTERNSHIPS_API_KEY = RAPIDAPI_KEY
    GOOGLE_JOBS_API_KEY = RAPIDAPI_KEY

    # Groq API — used for AI Tech Interview (llama-3.3-70b-versatile)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

    # Amazon Bedrock — Primary LLM Strategy
    BEDROCK_API_KEY = os.getenv('BEDROCK_API_KEY', '')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

    # Adzuna API
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '')
    ADZUNA_APP_KEY = os.getenv('ADZUNA_APP_KEY', '')

    # AWS S3 Storage & Polly
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME', '')





