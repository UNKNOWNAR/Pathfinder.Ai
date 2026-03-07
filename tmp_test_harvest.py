import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from flask import Flask
from services.harvester import _fetch_source_raw, _process_job_items
from models import db

app = Flask(__name__)
app.config['ADZUNA_APP_ID'] = 'test'
app.config['ADZUNA_APP_KEY'] = 'test'

with app.app_context():
    print("Testing RemoteOK...")
    raw, calls = _fetch_source_raw("RemoteOK", app.config)
    print(f"Fetched {len(raw)} raw jobs from {calls} calls")
    if raw:
        print(f"Sample: {raw[0]['title']} @ {raw[0]['company']}")
    
    # We should add INDIA_CITIES, etc to verify if things don't crash.
    # We won't actually insert to DB as that requires a real DB connection.
