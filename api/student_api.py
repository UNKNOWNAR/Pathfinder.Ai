from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import db
from models.students import Student
from models.user import User
from models import cache

class StudentAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        cache_key = f"student_{user_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data, 200

        student = Student.query.filter_by(user_id=user_id).first()
        if student:
            cache.set(cache_key, student.to_dict())
            return student.to_dict(), 200
        else:
            return {'message': 'Student record not found'}, 404

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        student = Student.query.filter_by(user_id=user_id).first()
        payload = request.get_json()
        
        if student:
            if not payload:
                return {'message': 'No data provided'}, 400
            
            # ── SYNC LOGIC ──
            user = User.query.get(user_id)
            if 'email' in payload and payload['email'] != user.email:
                # Uniqueness check to prevent 500 IntergrityError
                existing = User.query.filter(User.email == payload['email'], User.user_id != user_id).first()
                if existing:
                    return {'message': 'This email address is already in use by another account.'}, 409
                user.email = payload['email']
                
            # Security: Prevent students from changing their registered name (username)
            if 'name' in payload:
                del payload['name']

            student.updateData(payload)
            cache.delete(f"student_{user_id}") 
            cache.delete(f"student_drives_{user_id}")
            db.session.commit()
            return {'message': 'Student profile updated (Note: Name changes require Admin intervention)'}, 200
        else:
            # Create a new student entry if it doesn't exist
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return {'message': 'User accounts mismatch'}, 404
                
            student = Student(user_id=user_id, name=user.username, email=user.email)
            student.updateData(payload)
            cache.delete(f"student_{user_id}") 
            cache.delete(f"student_drives_{user_id}")
            db.session.add(student)
            db.session.commit()
            return {'message': 'Student record created successfully'}, 201

class StudentStatsAPI(Resource):
    @jwt_required()
    def get(self):
        """Dashboard counts for student progress"""
        from models.application import Application
        user_id = get_jwt_identity()
        applied = Application.query.filter_by(student_id=user_id).count()
        shortlisted = Application.query.filter(Application.student_id == user_id, Application.status.ilike('shortlisted')).count()
        selected = Application.query.filter(Application.student_id == user_id, Application.status.ilike('selected')).count()
        return {
            'applied': applied,
            'shortlisted': shortlisted,
            'selected': selected
        }, 200

class StudentApplicationsAPI(Resource):
    @jwt_required()
    def get(self):
        """Full list of application history for the student"""
        from models.application import Application
        user_id = get_jwt_identity()
        apps = Application.query.filter_by(student_id=user_id).all()
        return [app.to_dict() for app in apps], 200

class StudentExportAPI(Resource):
    @jwt_required()
    def get(self):
        """Student triggers export of their own application history via email"""
        user_id = get_jwt_identity()
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return {'message': 'Student not found'}, 404
        
        from services.AdminStudentCSV import export_student_history
        task = export_student_history.delay(user_id, student.email)
        return {"task_id": task.id, "message": f"Exporting history to {student.email}..."}, 200