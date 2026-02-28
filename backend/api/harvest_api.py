from flask import current_app, request
from flask_restful import Resource
from api.admin_api import admin_required
from models import db
from models.user import User
from models.job import Job, HarvestLog
from services.harvester import harvest_remotive_jobs


class AdminStats(Resource):
    @admin_required
    def get(self):
        students  = User.query.filter_by(role='student').count()
        companies = User.query.filter_by(role='company').count()
        jobs      = Job.query.count()
        return {
            'students':  students,
            'companies': companies,
            'jobs':      jobs,
        }, 200


class AdminHarvest(Resource):
    @admin_required
    def post(self):
        harvest_remotive_jobs(current_app._get_current_object())
        return {'message': 'Harvest started in background.'}, 202


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
