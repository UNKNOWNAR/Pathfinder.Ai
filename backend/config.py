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

    HF_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    if not HF_TOKEN:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is missing in the .env file.")

    RAPIDAPI_GLASSDOOR_KEY = os.getenv('RAPIDAPI_GLASSDOOR_KEY', '')
