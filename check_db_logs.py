from app import app
from models import db
from models.job import HarvestLog

with app.app_context():
    logs = HarvestLog.query.order_by(HarvestLog.timestamp.desc()).limit(5).all()
    for log in logs:
        print(f"ID: {log.log_id} | Source: {log.source} | Status: {log.status} | Added: {log.jobs_added} | Time: {log.timestamp}")
