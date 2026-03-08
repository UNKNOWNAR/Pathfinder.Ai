import sys
import os

# Add the current directory and backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

    from services.harvester import SOURCES, _fetch_source_raw

    def test_all_sources():
        print("=== DATA HARVESTER EFFECTIVENESS TEST (V2) ===")
        
        # Mock app config from environment
        app_config = {
            "JSEARCH_API_KEY": os.getenv("JSEARCH_API_KEY"),
            "INTERNSHIPS_API_KEY": os.getenv("INTERNSHIPS_API_KEY"),
            "GOOGLE_JOBS_API_KEY": os.getenv("GOOGLE_JOBS_API_KEY"),
            "ADZUNA_APP_ID": os.getenv("ADZUNA_APP_ID"),
            "ADZUNA_APP_KEY": os.getenv("ADZUNA_APP_KEY")
        }

        results = {}

        for source_id in SOURCES.keys():
            print(f"\n[TESTING] Source: {source_id}...")
            try:
                # We only fetch raw data to check if the connection and API work
                raw_data, api_calls = _fetch_source_raw(source_id, app_config)
                count = len(raw_data)
                
                if count > 0:
                    print(f"✅ SUCCESS: Found {count} raw jobs (Calls made: {api_calls})")
                    results[source_id] = {"status": "ACTIVE", "count": count}
                    # Print a sample job title if available
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        sample = raw_data[0]
                        title = "N/A"
                        if isinstance(sample, dict):
                            title = sample.get('title') or sample.get('job_title') or sample.get('title')
                        print(f"   Sample Job Found: {title}")
                else:
                    print(f"⚠️  WARNING: Connected but found 0 jobs (Check filters/keywords/API keys)")
                    results[source_id] = {"status": "ZERO_RESULTS", "count": 0}
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                results[source_id] = {"status": "ERROR", "error": str(e)}

        print("\n" + "="*40)
        print("FINAL HARVESTER REPORT")
        print("="*40)
        for src, res in results.items():
            status = res['status']
            count = res.get('count', 0)
            print(f"{src:15} | {status:12} | Jobs: {count}")
        print("="*40)

    if __name__ == "__main__":
        test_all_sources()
except Exception as e:
    print(f"Bootstrap failed: {e}")
