from flask import Flask
from models import db
from models.user import User
from config import Config
from flask_security import Security
from flask_security.utils import hash_password as fs_hash_password
from flask_restful import Api
from user_datastore import user_datastore
from api import init_routes
from flask_jwt_extended import JWTManager
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Security(app, user_datastore)
    JWTManager(app)

    api = Api(app)
    return app, api

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                active=True
            )
            admin.password = fs_hash_password('admin')
            db.session.add(admin)
            db.session.commit()

app, api = create_app()
CORS(app)
init_db()
init_routes(api)

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
