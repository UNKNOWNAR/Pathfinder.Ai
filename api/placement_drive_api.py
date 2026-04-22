from flask import request
from models import db, Company, PlacementDrive, Application, Student
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_restful import Resource
from models import cache

class CreateDriveAPI(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company access required'}, 403

        user_id = get_jwt_identity()
        data = request.get_json()
        company = Company.query.filter_by(user_id=user_id).first()
        
        if not company or company.status != 'approved':
            return {'message': 'Your account is pending admin approval.'}, 403
            
        drive = PlacementDrive(
            company_id=company.company_id,
            company_name=company.name,
            job_title=data.get('job_title'),
            job_description=data.get('job_description'),
            eligible_branch=data.get('eligible_branch'),
            cgpa_required=data.get('cgpa_required', 0.0),
            eligible_year=data.get('eligible_year'),
            status='pending'
        )
        db.session.add(drive)
        db.session.commit()
        return {'message': 'Placement drive posted and awaiting admin approval.'}, 201

    @jwt_required()
    def get(self, drive_id=None):
        """Company views their own drives OR applicants for a specific drive"""
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company access required'}, 403
        
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {'message': 'Company profile not found'}, 404

        if drive_id:
            # View applicants for a specific drive
            drive = PlacementDrive.query.filter_by(drive_id=drive_id, company_id=company.company_id).first()
            if not drive:
                return {'message': 'Drive not found or access denied'}, 404

            applications = Application.query.filter_by(drive_id=drive_id).all()

            # Enrich with student names for the UI
            result = []
            for app in applications:
                app_data = app.to_dict()
                student = Student.query.get(app.student_id)
                app_data['student_name'] = student.name if student else "Unknown"
                result.append(app_data)

            return {'applicants': result}, 200

        # List all drives created by this company
        drives = PlacementDrive.query.filter_by(company_id=company.company_id).all()
        return [d.to_dict() for d in drives], 200

    @jwt_required()
    def delete(self, drive_id):
        """Company deletes their drive"""
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company Role Required'}, 403
            
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {'message': 'Company profile not found'}, 404

        drive = PlacementDrive.query.get(drive_id)

        if not drive:
            return {'message': 'Drive not found'}, 404

        if drive.company_id != company.company_id:
            return {'message': 'Access Denied'}, 403
            
        db.session.delete(drive)
        db.session.commit()
        return {'message': 'Drive deleted successfully'}, 200
    
class ApplicationStatusAPI(Resource):
    @jwt_required()
    def put(self,application_id):
        """Company updates application status"""
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company Role Required'}, 403
            
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {'message': 'Company profile not found'}, 404

        data = request.get_json()
        new_status = data.get('status')

        application = Application.query.filter_by(application_id=application_id).first()
        if not application:
            return {'message': 'Application not found'}, 404

        if application.drive.company_id != company.company_id:
            return {'message': 'Access Denied'}, 403
            
        application.status = new_status
        db.session.commit()

        # If status is Selected/selected, trigger Offer Letter PDF task
        if new_status.lower() == 'selected':
            from services.AdminStudentCSV import send_offer_letter
            student = Student.query.get(application.student_id)
            drive = PlacementDrive.query.get(application.drive_id)
            if student and drive:
                send_offer_letter.delay(
                    student.name, 
                    student.email, 
                    drive.job_title, 
                    drive.company_name
                )
                
        return {'message': 'Application status updated successfully'}, 200

class StudentDrivesAPI(Resource):
    @jwt_required()
    def get(self):
        """The core Filtered List for students"""
        claims = get_jwt()
        
        if claims.get('role') != 'student':
            return {'message': 'Student Role Required'}, 403
            
        user_id = get_jwt_identity()
        cache_key = f"student_drives_{user_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data, 200

        student = Student.query.get(user_id)
        if not student:
            return {'message': 'Student profile not found'}, 404

        # Query only approved drives from ACTIVE companies
        query = PlacementDrive.query.join(Company, PlacementDrive.company_id == Company.company_id)\
            .filter(PlacementDrive.status == 'approved', Company.status == 'approved')
        
        # We also need to check if the User (account) itself is active
        from models.user import User
        active_company_ids = [c.company_id for c in Company.query.join(User).filter(User.active == True, Company.status == 'approved').all()]
        
        drives = query.filter(PlacementDrive.company_id.in_(active_company_ids)).all()
        applied_drive_ids = {app.drive_id for app in student.applications}
        eligible = []
        for d in drives:
            # Skip if already applied
            if d.drive_id in applied_drive_ids:
                continue
            # CGPA Check
            if student.cgpa < d.cgpa_required:
                continue
            # Branch Check (optional logic: d.eligible_branch might be 'All')
            if d.eligible_branch and d.eligible_branch != 'All' and d.eligible_branch != student.branch:
                continue
            eligible.append(d.to_dict())
            
        cache.set(cache_key, eligible)
        return eligible, 200

    @jwt_required()
    def put(self):
        """Student Apply to Drive"""
        claims = get_jwt()
        if claims.get('role') != 'student':
            return {'message': 'Student access required'}, 403
            
        user_id = get_jwt_identity()
        data = request.get_json()
        drive_id = data.get('drive_id')
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive or drive.status != 'approved':
            return {'message': 'Drive is not available for applications.'}, 404
            
        # Security: Prevent applying to drives of DEACTIVATED companies
        from models.user import User
        company_user = User.query.get(drive.company_id) # company_id is the user_id
        if not company_user or not company_user.active:
            return {'message': 'This drive is no longer accepting applications (Company Deactivated).'}, 403
            
        student = Student.query.get(user_id)
        if not student:
            return {'message': 'Student profile not found'}, 404

        # Gatekeeper: Eligibility Validation (CGPA + Branch + Batch Year)
        if student.cgpa < drive.cgpa_required:
            return {'message': 'You do not meet the minimum CGPA requirement.'}, 400
            
        if drive.eligible_branch and drive.eligible_branch != 'All' and drive.eligible_branch != student.branch:
            return {'message': 'You do not belong to the eligible branch for this drive.'}, 400
            
        if drive.eligible_year and drive.eligible_year != student.batch_year:
           return {'message': f'Only candidates from the {drive.eligible_year} batch are eligible.'}, 400
            
        # Deduplication
        if Application.query.filter_by(student_id=user_id, drive_id=drive_id).first():
            cache_key = f"student_drives_{user_id}"
            cache.delete(cache_key)
            return {'message': 'Already applied.'}, 409

        new_app = Application(student_id=user_id, drive_id=drive_id, status='Applied')
        db.session.add(new_app)
        db.session.commit()
        
        # Invalidate the cache so the list updates removing this drive
        cache_key = f"student_drives_{user_id}"
        cache.delete(cache_key)
        
        return {'message': 'Application submitted successfully!'}, 201

class AdminDriveAPI(Resource):
    @jwt_required()
    def patch(self, drive_id):
        """Admin flipping status from pending to approved"""
        if get_jwt().get('role') != 'admin':
            return {'message': 'Admin Access Required'}, 403
            
        data = request.get_json()
        drive = PlacementDrive.query.get(drive_id)
        if not drive:
            return {'message': 'Drive not found'}, 404
        drive.status = data.get('status') # 'approved' or 'rejected'
        db.session.commit()
        
        # FIX: Global Cache Invalidation - New drive approved means all students should see it
        from models import cache
        cache.clear() # Clears all listing caches to ensure students see the new drive immediately
        
        return {'message': 'Drive status updated'}, 200

class CompanyExportAPI(Resource):
    @jwt_required()
    def get(self, drive_id):
        """
        Triggers CSV export for applicants and sends to the logged-in company.
        URL: /company/export/drive/<drive_id>
        """
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company Role Required'}, 403
            
        from services.AdminStudentCSV import export_resource_csv
        from models import Company
        
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        to_email = company.email if company else ""
        
        task = export_resource_csv.delay('applicants', to_email, drive_id=drive_id)
        return {"task_id": task.id, "message": f"Export in progress (sending to {to_email})..."}, 200

class CompanyProfileAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company Role Required'}, 403
            
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {'message': 'Company profile not found'}, 404
        return company.to_dict(), 200

class CompanyStatsAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company Role Required'}, 403
            
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {'message': 'Company profile not found'}, 404
            
        drive_ids = [d.drive_id for d in PlacementDrive.query.filter_by(company_id=company.company_id).all()]
        
        selected = 0
        shortlisted = 0
        pending = 0
        applied = 0
        
        if drive_ids:
            applications = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
            applied = len(applications)
            for app in applications:
                s = app.status.lower()
                if s == 'selected':
                    selected += 1
                elif s == 'shortlisted':
                    shortlisted += 1
                elif s == 'applied' or s == 'pending':
                    pending += 1
                    
        return {
            'selected': selected,
            'shortlisted': shortlisted,
            'pending': pending,
            'total_applied': applied,
            'total_drives': len(drive_ids)
        }, 200

class CompanyAllApplicantsAPI(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Company Role Required'}, 403
            
        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return {'message': 'Company profile not found'}, 404
            
        drive_ids = [d.drive_id for d in PlacementDrive.query.filter_by(company_id=company.company_id).all()]
        
        result = []
        if drive_ids:
            applications = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
            for app in applications:
                app_data = app.to_dict()
                student = Student.query.get(app.student_id)
                drive = PlacementDrive.query.get(app.drive_id)
                app_data['student_name'] = student.name if student else "Unknown"
                app_data['job_title'] = drive.job_title if drive else "Unknown"
                result.append(app_data)
                
        # Sort by date descending
        result.sort(key=lambda x: x['date'], reverse=True)
        return {'applicants': result}, 200