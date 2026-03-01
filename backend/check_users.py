from app import app
from models.user import User

with app.app_context():
    users = User.query.all()
    print('--- Users ---')
    for u in users:
        print(f'User: {u.email} | Active: {u.active} | Role: {getattr(u, "role", "None")}')
