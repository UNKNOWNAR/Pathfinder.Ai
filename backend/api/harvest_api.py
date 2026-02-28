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

        return {
            'students':  students,
            'companies': companies,
            'jobs':      jobs,
            'sources':   sources_breakdown,
        }, 200


class AdminHarvest(Resource):
    @admin_required
    def post(self):
        data = request.get_json(silent=True) or {}
        source = data.get('source', 'all')
        app = current_app._get_current_object()

        if source == 'all':
            harvest_all(app)
        else:
            harvest_source(app, source)

        return {'message': f'Harvest started for {source} in background.'}, 202


class AdminLogs(Resource):
    @admin_required
    def get(self):
        logs = HarvestLog.query.order_by(HarvestLog.timestamp.desc()).limit(20).all()
        return [
            {
                'log_id':     l.log_id,
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
