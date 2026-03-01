import hashlib
import logging

logger = logging.getLogger(__name__)

# Constants for reuse
FRESHER_KEYWORDS = {
    "junior", "fresher", "entry level", "entry-level", "graduate",
    "trainee", "associate", "0-1 year", "0-2 year", "new grad",
}

def make_job_hash(title: str, company: str) -> str:
    """Generates a unique SHA-256 hash for a job title and company."""
    raw = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def is_fresher_role(title: str) -> bool:
    """Checks if a job title matches common fresher/entry-level keywords."""
    title_lower = (title or "").lower()
    return any(kw in title_lower for kw in FRESHER_KEYWORDS)
