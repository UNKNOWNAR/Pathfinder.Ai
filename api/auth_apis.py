from flask_restful import Resource
from flask import request
from models.user import db,User
from models.profile import Profile
from user_datastore import user_datastore
from sqlalchemy import or_
from flask_jwt_extended import create_access_token, jwt_required

class LoginUser(Resource):
    def post(self):
        login_data = request.get_json()

        if not login_data or not login_data.get('username_or_email') or not login_data.get('password'):
            result = {
                'message': 'No data provided',
                'status': 'error'
            }
            return result, 400

        identity = login_data.get('username_or_email')
        password = login_data.get('password')

        user = User.query.filter(
            or_(User.username == identity, User.email == identity)
        ).first()

        if not user:
            result = {
                'message': 'User not found',
                'status': 'error'
            }
            return result, 404
        
        if not user.check_password(password):
            result = {
                'message': 'Invalid password',
                'status': 'error'
            }
            return result, 401
        
        if not user.active:
            result = {
                'message': 'User is not active',
                'status': 'error'
            }
            return result, 403
        
        access_token = create_access_token(identity=str(user.user_id),additional_claims={'role': user.role})
        
        result = {
            'message': 'Login successful',
            'access_token': access_token
        }
        return result, 200

class LogoutUser(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'Logout successful'}, 200

class SignUpUser(Resource):
    def post(self):
        register_data = request.get_json()

        if not register_data or not all(k in register_data for k in ('username', 'email', 'password', 'role')):
            result = {
                'message': 'No data provided',
                'status': 'error'
            }
            return result, 400

        role = register_data.get('role')
        if role == 'admin':
            result = {
                'message': 'Admin registration not allowed',
                'status': 'error'
            }
            return result, 403

        username = register_data.get('username')
        email = register_data.get('email')
        password = register_data.get('password')

        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            conflict_field = "Username" if existing_user.username == username else "Email"
            
            result = {
                'message': f'{conflict_field} already exists',
                'status': 'error'
            }
            return result, 409

        active = True if role == 'student' else False
        user = user_datastore.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            active=active
        )
        db.session.flush() #forces SQLite to assign user_id NOW
        db.session.add(Profile(user_id=user.user_id,name = user.username,email = user.email))
        db.session.commit()
        result = {
            'message': 'User registered successfully',
            'status': 'success'
        }
        return result, 201