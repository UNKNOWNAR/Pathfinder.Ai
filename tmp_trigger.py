import sys
import os
sys.path.append('/home/ubuntu/Pathfinder.Ai/backend')
from app import app
from services.harvester import _run_harvest

with app.app_context():
    print("Starting Manual RSS Harvest (WeWorkRemotely)...")
    _run_harvest(app, source='WeWorkRemotely')
    print("Done.")
