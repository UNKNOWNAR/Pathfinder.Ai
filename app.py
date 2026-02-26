from flask import Flask
from models import db
from routes.generate_resume import resume_bp  # Import your new blueprint
from config import Config
from flask_security import Security
from user_datastore import user_datastore

def create_app():
    app = Flask(__name__)
    return app