from flask_restful import Resource
from flask import request
from flask_jwt_extended import get_jwt_identity,jwt_required
import json
from models import db
from models.profile import Profile
from services.embedding import store_student_embedding

class ProfileAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        student = Profile.query.filter_by(user_id=user_id).first()
        if student:
            return student.to_dict(),200
        else:
            return {'message': 'Student not found'}, 404

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            payload = request.get_json()
            if not payload:
                return {'message': 'No data provided'}, 400
            profile.updateData(payload)

            # Re-generate vector embedding based on updated profile
            # We convert skills array to string if it exists for the embedding generator
            skills_text = ""
            if profile.skills:
                skills_text = ", ".join(profile.skills) if isinstance(profile.skills, list) else str(profile.skills)

            vector = store_student_embedding(
                student_id=user_id,
                skills=skills_text,
                headline=profile.headline,
                summary=profile.summary
            )

            # We store it in PG as a JSON array (pgvector migration ready)
            profile.embedding = vector

            db.session.commit()
            return {'message': 'Profile updated successfully'}, 200
        else:
            return {'message': 'Profile not found'}, 404
