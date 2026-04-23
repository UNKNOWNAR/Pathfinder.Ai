from flask import request
from flask_restful import Resource
from api.admin_api import admin_required
from models import db
from models.user import User
from models.profile import Profile


class AdminStudents(Resource):
    @admin_required
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('q', '', type=str).strip()

        query = User.query.filter_by(role='student')
        if search:
            like = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.username.ilike(like),
                    User.email.ilike(like),
                )
            )

        paginated = query.order_by(User.user_id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        students = []
        for u in paginated.items:
            profile = Profile.query.filter_by(user_id=u.user_id).first()
            students.append({
                'user_id': u.user_id,
                'username': u.username,
                'email': u.email,
                'active': u.active,
                'name': profile.name if profile else u.username,
                'headline': profile.headline if profile else None,
                'skills': profile.skills if profile else None,
                'location': profile.location if profile else None,
            })

        return {
            'total': paginated.total,
            'pages': paginated.pages,
            'page': paginated.page,
            'students': students,
        }, 200
