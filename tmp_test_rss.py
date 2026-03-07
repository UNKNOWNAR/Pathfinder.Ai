import sys
import os
sys.path.append('/home/ubuntu/Pathfinder.Ai/backend')
from services.rss_sources import fetch_remoteok_jobs, fetch_weworkremotely_jobs

try:
    print("Testing RemoteOK...")
    r = fetch_remoteok_jobs()
    print(f"RemoteOK: found {len(r)} jobs")
    if r: print(f"Sample: {r[0]['title']}")
except Exception as e:
    print(f"RemoteOK Failed: {e}")

try:
    print("\nTesting WeWorkRemotely...")
    w = fetch_weworkremotely_jobs()
    print(f"WeWorkRemotely: found {len(w)} jobs")
    if w: print(f"Sample: {w[0]['title']}")
except Exception as e:
    print(f"WeWorkRemotely Failed: {e}")
