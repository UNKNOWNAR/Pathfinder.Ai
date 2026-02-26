from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)#255 size to store large size of hashing password
    # Roles: 'admin', 'company', 'student'
    role = db.Column(db.String(80), nullable=False,default='student')
    fs_uniquifier = db.Column(db.String(255), nullable=False,unique=True,default=lambda: str(uuid.uuid4()))

    # Status: 'active', 'pending', 'blacklisted'
    status = db.Column(db.String(80), nullable=False,default='pending')

    @property
    def is_active(self):
        return self.status != 'blacklisted'
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

