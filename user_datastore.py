#user_datastore.py
from flask_security import SQLAlchemyUserDatastore
from models import db,User

user_datastore = SQLAlchemyUserDatastore(db,User)
