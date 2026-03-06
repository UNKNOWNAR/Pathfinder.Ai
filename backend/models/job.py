from . import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'job'

    job_id      = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(255), nullable=False)
    company     = db.Column(db.String(255), nullable=False)
    location    = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    source      = db.Column(db.String(80), nullable=False)   # e.g. 'Adzuna', 'LinkedIn'
    url         = db.Column(db.String(512), nullable=True)
    hash        = db.Column(db.String(64), unique=True, nullable=False)  # SHA-256 dedup key

    # Using JSON fallback since pgvector is not installed natively
    embedding   = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Job {self.title} @ {self.company}>'


class HarvestLog(db.Model):
    __tablename__ = 'harvest_log'

    log_id     = db.Column(db.Integer, primary_key=True)
    source     = db.Column(db.String(80), nullable=False, default='all')  # 'all', 'Remotive', 'Arbeitnow', 'Glassdoor', 'LinkedIn'
    status     = db.Column(db.String(20), nullable=False, default='running')  # 'running', 'completed', 'failed'
    jobs_added = db.Column(db.Integer, nullable=False, default=0)
    api_calls  = db.Column(db.Integer, nullable=False, default=1)  # Tracks how many API requests were made during this run
    timestamp  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<HarvestLog {self.log_id} — {self.source} — {self.status}>'
