from functools import wraps
from flask import request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 1. Check for System API Key (for automated internal tasks like daily harvest)
        api_key = request.headers.get('X-System-API-Key')
        system_key = current_app.config.get('SYSTEM_API_KEY')

        if system_key and api_key == system_key:
            return fn(*args, **kwargs)

        # 2. Fallback to JWT Admin requirement
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return {'message': 'Admin access required'}, 403
            return fn(*args, **kwargs)
        except Exception:
            return {'message': 'Authentication required'}, 401

    return wrapper
