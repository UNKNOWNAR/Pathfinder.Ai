from flask_restful import Resource
from flask import request
from models import db
from models.user import User
from models.company import Company
from user_datastore import user_datastore
from sqlalchemy import or_
from api.admin_api import admin_required


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

