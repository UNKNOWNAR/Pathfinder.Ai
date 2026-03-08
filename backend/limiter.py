from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize standard Limiter using the user's IP address
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"] # Generous default safeguards
)
