from app import app
from models import db
from models.user import User
from models.students import Student
from models.company import Company
from models.placement import PlacementDrive
from models.application import Application
from sqlalchemy import inspect

with app.app_context():
    for model in [User, Student, Company, PlacementDrive, Application]:
        inspector = inspect(model)
        print(f"Model: {model.__name__}")
        for rel in inspector.relationships:
            print(f"  Rel: {rel.key}, cascade: {rel.cascade}")
