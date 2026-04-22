from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_jwt_extended import get_jwt_identity

def get_jwt_or_ip():
    """Identifier for rate limiting: use User ID if logged in, else fallback to IP."""
    try:
        # We wrap in a try/except because if this is called before the request
        # context is fully initialized with JWT, it might throw a RuntimeError.
        user_id = get_jwt_identity()
        if user_id:
            return str(user_id)
    except:
        pass
    return get_remote_address()

# Initialize standard Limiter
limiter = Limiter(
    key_func=get_jwt_or_ip,
    default_limits=["1000 per day", "100 per hour"] # Generous default safeguards
)
