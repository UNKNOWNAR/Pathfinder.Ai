from flask import Flask
from models import db
from models.job import Job, HarvestLog
from sqlalchemy import func
from dotenv import load_dotenv
import os

load_dotenv('/home/ubuntu/Pathfinder.Ai/backend/.env')

app = Flask(__name__)
# Ensure we pick up the RDS URL
db_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
if not db_url:
    print("FATAL: DATABASE_URL not found in .env")
    exit(1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # 1. Check counts by source
    counts = db.session.query(Job.source, func.count(Job.job_id)).group_by(Job.source).all()
    print("--- COUNTS BY SOURCE ---")
    for s, c in counts:
        print(f"{s}: {c}")

    # 2. Check last 5 jobs
    print("\n--- RECENTLY ADDED JOBS ---")
    jobs = Job.query.order_by(Job.job_id.desc()).limit(5).all()
    for j in jobs:
        print(f"[{j.source}] {j.title} @ {j.company} | Created: {j.created_at}")
