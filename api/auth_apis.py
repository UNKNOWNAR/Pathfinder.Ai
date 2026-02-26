from flask_restful import Resource
from flask import request,jsonify
from models.user import User
from user_datastore import user_datastore

class LoginUser(Resource):
    def post(self):
        login_data = request.get_json()

        if not login_data or not login_data.get('username_or_email') or not login_data.get('password'):
            result = {
                'message': 'No data provided',
                'status': 'error'
            }
            return jsonify(result), 400        

        username_or_email = login_data.get('username_or_email')
        password = login_data.get('password')

        user = user_datastore.find_user_or_(username_or_email=username_or_email)
        if not user:
            result = {
                'message': 'User not found',
                'status': 'error'
            }
            return jsonify(result), 404
        
        if not user.check_password(password):
            result = {
                'message': 'Invalid password',
                'status': 'error'
            }
            return jsonify(result), 401
        
        return {'message': 'Login successful'}