from flask import Flask
from models import db
from config import Config
from flask_security import Security
from user_datastore import user_datastore

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app