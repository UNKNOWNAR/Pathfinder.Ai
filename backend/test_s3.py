import os
import boto3
from dotenv import load_dotenv

# Set the path to the .env file explicitly if needed
load_dotenv(dotenv_path='.env')

try:
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    bucket = os.getenv('AWS_S3_BUCKET_NAME')
    
    print(f"Region: {region}")
    print(f"Bucket: {bucket}")
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=5)
    print(f"Connection Successful!")
    print(f"Found {len(resp.get('Contents', []))} objects.")
    for obj in resp.get('Contents', []):
        print(f" - {obj['Key']}")
        
except Exception as e:
    print(f"ERROR: {e}")
