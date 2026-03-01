from flask import current_app, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
from api.admin_api import admin_required
from models import db
from models.user import User
from models.job import Job, HarvestLog
from services.harvester import harvest_all, harvest_source


class AdminStats(Resource):
    @admin_required
    def get(self):
        from sqlalchemy import func
        students  = User.query.filter_by(role='student').count()
        companies = User.query.filter_by(role='company').count()
        jobs      = Job.query.count()

        # Group jobs by source
        sources_query = db.session.query(Job.source, func.count(Job.job_id)).group_by(Job.source).all()
        sources_breakdown = {s: c for s, c in sources_query}

        # Extract job roles dynamically
        roles_query = db.session.execute(db.text("""
            SELECT
                CASE
                    WHEN LOWER(title) LIKE '%software engineer%' THEN 'Software Engineer'
                    WHEN LOWER(title) LIKE '%data scientist%' THEN 'Data Scientist'
                    WHEN LOWER(title) LIKE '%data engineer%' THEN 'Data Engineer'
                    WHEN LOWER(title) LIKE '%machine learning%' THEN 'ML Engineer'
                    WHEN LOWER(title) LIKE '%frontend%' THEN 'Frontend'
                    WHEN LOWER(title) LIKE '%backend%' THEN 'Backend'
                    WHEN LOWER(title) LIKE '%full stack%' THEN 'Full Stack'
                    WHEN LOWER(title) LIKE '%intern%' THEN 'Internship'
                    ELSE 'Other'
                END as role_type,
                COUNT(*) as count
            FROM job
            GROUP BY role_type
        """)).fetchall()

        roles_breakdown = {row[0]: row[1] for row in roles_query}

        return {
            'students':  students,
            'companies': companies,
            'jobs':      jobs,
            'sources':   sources_breakdown,
            'roles':     roles_breakdown
        }, 200


class AdminHarvest(Resource):
    @admin_required
    def post(self):
        data = request.get_json(silent=True) or {}
        source = data.get('source', 'all')
        roles = data.get('roles', [])
        locations = data.get('locations', [])

        app = current_app._get_current_object()

        if source == 'all':
            harvest_all(app, roles, locations)
        else:
            harvest_source(app, source, roles, locations)

        return {'message': f'Harvest started for {source} in background.'}, 202


class AdminQuotas(Resource):
    @admin_required
    def get(self):
        from sqlalchemy import func
        from datetime import datetime, timezone, timedelta

        # Calculate start of current month in UTC
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        # Get sum of api_calls per source for this month
        usage_query = db.session.query(
            HarvestLog.source,
            func.sum(HarvestLog.api_calls)
        ).filter(
            HarvestLog.timestamp >= start_of_month
        ).group_by(HarvestLog.source).all()

        usage = {s: int(c or 0) for s, c in usage_query}

        # Monthly limits based on RapidAPI plans
        limits = {
            "LinkedIn": 200,
            "Internships": 200,
            "GoogleJobs": 100,
            "Remotive": -1, # Unlimited
            "Arbeitnow": -1 # Unlimited
        }

        return {
            "usage": usage,
            "limits": limits
        }, 200


class AdminLogs(Resource):
    @admin_required
    def get(self):
        logs = HarvestLog.query.order_by(HarvestLog.timestamp.desc()).limit(20).all()
        return [
            {
                'log_id':     l.log_id,
                'source':     l.source,
                'status':     l.status,
                'jobs_added': l.jobs_added,
                'timestamp':  l.timestamp.isoformat(),
            }
            for l in logs
        ], 200


class AdminJobsList(Resource):
    @admin_required
    def get(self):
        page     = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search   = request.args.get('q', '', type=str).strip()

        query = Job.query
        if search:
            like = f"%{search}%"
            query = query.filter(
                db.or_(
                    Job.title.ilike(like),
                    Job.company.ilike(like),
                    Job.location.ilike(like),
                )
            )

        paginated = query.order_by(Job.job_id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'total': paginated.total,
            'pages': paginated.pages,
            'page':  paginated.page,
            'jobs':  [
                {
                    'job_id':   j.job_id,
                    'title':    j.title,
                    'company':  j.company,
                    'location': j.location,
                    'source':   j.source,
                    'url':      j.url,
                }
                for j in paginated.items
            ]
        }, 200


class JobsList(Resource):
    @jwt_required()
    def get(self):
        # We need to ensure that the user accessing this endpoint is indeed a student
        claims = get_jwt()
        if claims.get('role') != 'student':
            return {'message': 'Only students can view the job feed.'}, 403

        page     = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search   = request.args.get('q', '', type=str).strip()

        query = Job.query
        if search:
            like = f"%{search}%"
            query = query.filter(
                db.or_(
                    Job.title.ilike(like),
                    Job.company.ilike(like),
                    Job.location.ilike(like),
                )
            )

        paginated = query.order_by(Job.job_id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'total': paginated.total,
            'pages': paginated.pages,
            'page':  paginated.page,
            'jobs':  [
                {
                    'job_id':   j.job_id,
                    'title':    j.title,
                    'company':  j.company,
                    'location': j.location,
                    'source':   j.source,
                    'url':      j.url,
                    'description': j.description
                }
                for j in paginated.items
            ]
        }, 200
