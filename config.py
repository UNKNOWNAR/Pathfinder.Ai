from dotenv import load_dotenv
load_dotenv()

class Config:
    DEBUG = True
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False