import io
from flask import Blueprint, request, jsonify, send_file
from services.llm_service import LLMService
from services.compiler_service import CompilerService
from models.profile import Profile
from flask_jwt_extended import jwt_required,get_jwt_identity

class GenerateResume(Resource):
    @jwt_required()
    def post(self,jd_text):
        user_id = get_jwt_identity()
        student = Profile.query.filter_by(user_id=user_id).first()
        if not student:
            return {'message': 'Student not found'}, 404
    
