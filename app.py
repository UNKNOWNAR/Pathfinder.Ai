from flask import Flask
from models import db
from routes.generate_resume import resume_bp  # Import your new blueprint

def create_app():
    app = Flask(__name__)
    
    # Register your resume generation endpoint
    app.register_blueprint(resume_bp)
    
    return app