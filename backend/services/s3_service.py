"""
Storage Service — Cloudflare R2 Edition
=========================================
AWS S3 has been replaced with Cloudflare R2, which is S3-compatible.
R2 Free Tier: 10 GB storage, 1M write ops, 10M read ops per month.

Setup:
1. Go to dash.cloudflare.com → R2 → Create bucket
2. Go to R2 → Manage R2 API Tokens → Create API Token (with Object Read & Write)
3. Note your Account ID from the R2 dashboard URL
4. Set these env vars:
   - R2_ACCOUNT_ID
   - R2_ACCESS_KEY_ID
   - R2_SECRET_ACCESS_KEY
   - R2_BUCKET_NAME
"""
import os
import boto3
from botocore.exceptions import ClientError
import uuid
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """
    Storage service backed by Cloudflare R2.
    The boto3 SDK works identically — only the endpoint_url changes.
    """
    def __init__(self):
        account_id = os.getenv('R2_ACCOUNT_ID', '')
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            region_name='auto',  # R2 uses 'auto' as the region
        )
        self.bucket_name = os.getenv('R2_BUCKET_NAME')
        self.public_url_base = os.getenv('R2_PUBLIC_URL', '')  # e.g. https://pub-xxx.r2.dev
        self.environment = os.getenv('ENVIRONMENT', 'development')

    def _get_prefix(self, folder):
        return f"{self.environment}/{folder}"

    def upload_avatar(self, file_obj, filename, user_id):
        """Uploads a profile avatar to R2 and returns the object key."""
        try:
            ext = os.path.splitext(filename)[1].lower()
            safe_filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
            s3_key = f"{self._get_prefix('avatars')}/{safe_filename}"

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': self._get_content_type(filename)}
            )
            return s3_key
        except ClientError as e:
            logger.error(f"R2 Avatar Upload Error: {e}")
            return None

    def get_public_url(self, s3_key):
        """Returns a direct public URL for assets (requires R2 public bucket or custom domain)."""
        if not s3_key:
            return None
        if self.public_url_base:
            return f"{self.public_url_base.rstrip('/')}/{s3_key}"
        # Fallback: generate a presigned URL if no public domain is set
        return self.get_presigned_url(s3_key)

    def upload_resume_pdf(self, pdf_bytes, user_id):
        """Uploads a generated PDF resume to R2 and returns the object key."""
        try:
            safe_filename = f"resume_user_{user_id}_{uuid.uuid4().hex[:8]}.pdf"
            s3_key = f"{self._get_prefix('resumes')}/{safe_filename}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=pdf_bytes,
                ContentType='application/pdf'
            )
            return s3_key
        except ClientError as e:
            logger.error(f"R2 Resume Upload Error: {e}")
            return None

    def get_presigned_url(self, s3_key, expires_in=3600):
        """Generates a presigned URL for private assets like resumes (expires in 1 hour)."""
        if not s3_key:
            return None
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
        except ClientError as e:
            logger.error(f"R2 Presigned URL Error: {e}")
            return None

    def delete_file(self, s3_key):
        """Deletes a file from R2."""
        if not s3_key:
            return False
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            logger.error(f"R2 Delete Error: {e}")
            return False

    def _get_content_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
        }.get(ext, 'application/octet-stream')
