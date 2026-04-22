from flask_restful import Resource
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db
from models.profile import Profile
from services.embedding import store_student_embedding
from services.s3_service import S3Service

s3_service = S3Service()

def _format_profile_data(profile):
    data = profile.to_dict()
    
    # 1. Generate active presigned URL for avatar if it's stored in S3
    if data.get('avatar_url'):
        # If it's a raw S3 key (doesn't start with http)
        if not data['avatar_url'].startswith('http'):
            data['avatar_url'] = s3_service.get_presigned_url(data['avatar_url'])
        # If it's an old direct public S3 URL, extract the key and sign it
        elif 'amazonaws.com' in data['avatar_url'] and '?' not in data['avatar_url']:
            s3_key = data['avatar_url'].split('amazonaws.com/')[-1]
            data['avatar_url'] = s3_service.get_presigned_url(s3_key)
            
    # 2. Generate active presigned URLs for all resumes in history
    if data.get('resumes'):
        for resume in data['resumes']:
            if resume.get('s3_key'):
                resume['url'] = s3_service.get_presigned_url(resume['s3_key'])
                
    return data

class ProfileAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        student = Profile.query.filter_by(user_id=user_id).first()
        if student:
            return _format_profile_data(student), 200
        else:
            return {'message': 'Student not found'}, 404

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()

        if not profile:
            return {'message': 'Profile not found'}, 404

        # Handle multipart/form-data for avatar uploads
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Check for avatar file
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file.filename != '':
                    s3_key = s3_service.upload_avatar(file, file.filename, user_id)
                    if s3_key:
                        profile.avatar_url = s3_key

            # The rest of the form data might be JSON strings or individual fields
            # For this implementation, we handle the avatar upload via form-data
            # and expect the main profile updates to still come via JSON below or
            # as form fields.
            payload = request.form.to_dict()

            # Convert JSON strings back to objects if they are passed as form fields
            import json
            for key in ['skills', 'experience', 'education', 'projects', 'achievements']:
                if key in payload and isinstance(payload[key], str):
                    try:
                        payload[key] = json.loads(payload[key])
                    except json.JSONDecodeError:
                        pass
        else:
            payload = request.get_json()

        if payload:
            profile.updateData(payload)

        # Always try to generate embedding if we got past the not found check
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
        return {
            'message': 'Profile updated successfully',
            'profile': _format_profile_data(profile)
        }, 200

class ResumeResource(Resource):
    method_decorators = [jwt_required()]

    def delete(self, index):
        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {"message": "Profile not found"}, 404
        
        try:
            resumes = list(profile.resumes or [])
            if not (0 <= index < len(resumes)):
                return {"message": "Invalid resume index"}, 400
            
            resume = resumes.pop(index)
            s3_key = resume.get("s3_key")
            
            # Delete from S3
            if s3_key:
                try:
                    s3_service.delete_file(s3_key)
                except Exception as e:
                    import logging
                    logging.error(f"S3 Delete failed: {e}")
            
            profile.resumes = resumes
            db.session.commit()
            return {"message": "Resume deleted successfully", "resumes": _format_profile_data(profile)['resumes']}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def patch(self, index):
        data = request.get_json()
        new_filename = data.get("filename")
        if not new_filename:
            return {"message": "Filename required"}, 400
            
        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {"message": "Profile not found"}, 404

        try:
            resumes = list(profile.resumes or [])
            if not (0 <= index < len(resumes)):
                return {"message": "Invalid resume index"}, 400
                
            # Ensure it ends with .pdf
            if not new_filename.lower().endswith('.pdf'):
                new_filename += '.pdf'
                
            resumes[index]["filename"] = new_filename
            profile.resumes = resumes
            db.session.commit()
            return {"message": "Resume renamed successfully", "resumes": _format_profile_data(profile)['resumes']}, 200
        except Exception as e:
            return {"error": str(e)}, 500
