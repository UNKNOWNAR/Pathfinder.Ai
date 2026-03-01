from flask_restful import Resource
from flask import request
from models import db
from models.user import User
from models.job import Job
from models.company import Company
from user_datastore import user_datastore
from sqlalchemy import or_
from api.admin_api import admin_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.utils import make_job_hash
from services.embedding import store_job_embedding


class CompanyRegister(Resource):

    def post(self):
        data = request.get_json()

        if not data or not all(k in data for k in ('company_name', 'email', 'password')):
            return {'message': 'company_name, email, and password are required.'}, 400

        company_name = data['company_name'].strip()
        email = data['email'].strip()
        password = data['password']

        if not company_name or not email:
            return {'message': 'company_name and email cannot be empty.'}, 400

        existing = User.query.filter(
            or_(User.username == company_name, User.email == email)
        ).first()

        if existing:
            conflict = 'Email' if existing.email == email else 'Company name'
            return {'message': f'{conflict} already exists.'}, 409

        user = user_datastore.create_user(
            username=company_name,
            email=email,
            password=password,
            role='company',
            active=True,
        )
        db.session.flush()

        company = Company(
            user_id=user.user_id,
            name=company_name,
            is_approved=False,
        )
        db.session.add(company)
        db.session.commit()

        return {
            'message': 'Company registered successfully. Awaiting admin approval.',
            'company_id': company.company_id,
        }, 201


class AdminCompanies(Resource):
    @admin_required
    def get(self):
        # Join Company and User to get the email
        results = db.session.query(Company, User.email).join(User, Company.user_id == User.user_id).all()
        return [
            {
                'company_id': comp.company_id,
                'name': comp.name,
                'email': email,
                'is_approved': comp.is_approved,
                'created_at': comp.created_at.isoformat() if comp.created_at else None
            }
            for comp, email in results
        ], 200


class AdminCompanyApprove(Resource):
    @admin_required
    def post(self, company_id):
        company = Company.query.get_or_404(company_id)
        if company.is_approved:
            return {'message': 'Company is already approved.'}, 400

        company.is_approved = True
        db.session.commit()
        return {'message': f'Company {company.name} approved successfully.'}, 200


class CompanyJobs(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return {'message': 'Only companies can post jobs.'}, 403

        user_id = get_jwt_identity()
        company = Company.query.filter_by(user_id=user_id).first()

        if not company:
            return {'message': 'Company profile not found.'}, 404

        if not company.is_approved:
            return {'message': 'Your company account is pending approval by an admin. You cannot post jobs yet.'}, 403

        data = request.get_json()
        required_fields = ['title', 'description']
        if not data or not all(k in data for k in required_fields):
            return {'message': 'title and description are required fields.'}, 400

        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        location = data.get('location', '').strip() or 'Remote'
        url = data.get('url', '').strip()

        if not title or not description:
            return {'message': 'title and description cannot be empty.'}, 400

        # Use deduplication logic (from harvester)
        job_hash = make_job_hash(title, company.name)

        existing = Job.query.filter_by(hash=job_hash).first()
        if existing:
            return {'message': 'You have already posted this job (duplicate title).'}, 409

        new_job = Job(
            title=title,
            company=company.name,
            location=location,
            description=description,
            source="Direct",
            url=url,
            hash=job_hash
        )

        db.session.add(new_job)
        db.session.commit()

        # Generate embedding for the new job
        store_job_embedding(new_job.id, new_job.title, new_job.description)

        return {
            'message': 'Job posted successfully.',
            'job_id': new_job.id
        }, 201

