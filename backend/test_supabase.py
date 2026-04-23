import os
from dotenv import load_dotenv
from supabase import create_client

def test_connection():
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')

    print(f"Testing connection to: {url}")
    print(f"URL Length: {len(url) if url else 0}")

    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY missing from .env")
        return

    try:
        supabase = create_client(url, key)
        # Try to list buckets to verify the key
        buckets = supabase.storage.list_buckets()
        print("Successfully connected to Supabase!")
        print(f"Available buckets: {[b.name for b in buckets]}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
