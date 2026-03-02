
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.abspath('backend'))

from app import app
from models.job import Job, HarvestLog

with app.app_context():
    count = Job.query.filter_by(source='FaangWatch').count()
    print(f"Total FaangWatch Jobs: {count}")

    last_log = HarvestLog.query.filter_by(source='FaangWatch').order_by(HarvestLog.timestamp.desc()).first()
    if last_log:
        print(f"Last Log Status: {last_log.status}")
        print(f"Jobs Added: {last_log.jobs_added}")
        print(f"Timestamp: {last_log.timestamp}")
    else:
        print("No FaangWatch logs found.")
