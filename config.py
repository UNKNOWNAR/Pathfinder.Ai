from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    DEBUG = True
    SECRET_KEY = 'your-secret-key'
    SECURITY_PASSWORD_SALT = 'your-password-salt'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-jwt-secret-key'

    # Disable CSRF — this is a REST API using token-based auth, not forms
    WTF_CSRF_ENABLED = False
    SECURITY_WTF_CSRF_ENABLED = False

    # Move Flask-Security's built-in routes away from /login so our API can use it
    SECURITY_URL_PREFIX = '/security'

    HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is missing in the .env file.")

