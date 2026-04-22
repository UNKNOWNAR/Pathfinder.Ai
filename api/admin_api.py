from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from flask_restful import Resource
from models import db, User, Student, Company, PlacementDrive

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return {'message': 'Admin access required'}, 403
        return fn(*args, **kwargs)
    return wrapper

class AdminStatsAPI(Resource):
    @admin_required
    def get(self):
        student_count = Student.query.count()
        company_count = Company.query.count()
        placement_drive_count = PlacementDrive.query.count()
        return {
            'student_count': student_count,
            'company_count': company_count,
            'placement_drive_count': placement_drive_count
        }, 200

class AdminCompaniesAPI(Resource):
    @admin_required
    def get(self):
        companies = Company.query.all()
        result = []
        for c in companies:
            user = User.query.get(c.user_id)
            result.append({
                'user_id': c.user_id,
                'name': c.name,
                'status': c.status,
                'active': user.active if user else False
            })
        return result, 200

class AdminApproveCompanyAPI(Resource):
    @admin_required
    def post(self, company_id):
        company = Company.query.filter_by(user_id=company_id).first()
        if not company:
            return {'message': 'Company not found'}, 404

        user = User.query.get(company_id)
        if not user:
            return {'message': 'User not found'}, 404

        company.status = 'approved'
        user.active = True
        db.session.commit()
        
        from models import cache
        cache.clear()
        
        return {'message': 'Company approved successfully!'}, 200

class AdminStudentsAPI(Resource):
    @admin_required
    def get(self):
        students = Student.query.all()
        result = []
        for s in students:
            user = User.query.get(s.user_id)
            result.append({
                'user_id': s.user_id,
                'name': s.name,
                'branch': s.branch,
                'batch_year': s.batch_year,
                'active': user.active if user else False
            })
        return result, 200

class AdminToggleUserStatusAPI(Resource):
    @admin_required
    def post(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        if user.role == 'admin':
            return {'message': 'Cannot deactivate admin'}, 403
            
        user.active = not user.active
        db.session.commit()
        
        from models import cache
        cache.clear()
        
        status_text = "activated" if user.active else "deactivated"
        return {'message': f'User {status_text} successfully!', 'active': user.active}, 200

class AdminPendingDrivesAPI(Resource):
    @admin_required
    def get(self):
        """Returns all drives across all companies that need approval"""
        drives = PlacementDrive.query.all()
        return [d.to_dict() for d in drives], 200

class AdminExportAPI(Resource):
    @admin_required
    def get(self, target):
        """
        Triggers CSV export for 'students' or 'companies'
        URL: /admin/export/<string:target>
        """
        from services.AdminStudentCSV import export_resource_csv
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        admin_email = user.email if user else "admin@example.com"
        
        task = export_resource_csv.delay(target, admin_email)
        return {"task_id": task.id, "message": f"Exporting {target} to {admin_email}..."}, 200

class AdminMonthlyReportAPI(Resource):
    @admin_required
    def get(self):
        """Manually trigger the monthly report task"""
        from services.AdminStudentCSV import monthly_report_task
        task = monthly_report_task.delay()
        return {"task_id": task.id, "message": "Triggered monthly report generation..."}, 200
