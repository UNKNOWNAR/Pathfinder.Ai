from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security import UserMixin,RoleMixin,SQLAlchemyUserDatastore

class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)#255 size to store large size of hashing password
    # Roles: 'admin', 'company', 'student'
    role = db.Column(db.String(80), nullable=False,default='student')

    # Status: 'active', 'pending', 'blacklisted'
    status = db.Column(db.String(80), nullable=False,default='pending')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

