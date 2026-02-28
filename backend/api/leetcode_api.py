from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.profile import Profile
from services.leetcode_client import LeetCodeClient


class LeetCodeStats(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return {'message': 'Only students can view LeetCode stats.'}, 403

        user_id = get_jwt_identity()
        profile = Profile.query.filter_by(user_id=user_id).first()

        if not profile:
            return {'message': 'Profile not found.'}, 404

        username = profile.leetcode_username
        if not username or not username.strip():
            return {
                'message': 'No LeetCode username set. Update your profile first.',
                'no_username': True
            }, 400

        stats = LeetCodeClient.fetch_user_data(username.strip())

        if stats is None:
            return {
                'message': f'Could not fetch data for LeetCode user "{username}". Check if the username is correct.',
            }, 502

        return {'stats': stats}, 200
