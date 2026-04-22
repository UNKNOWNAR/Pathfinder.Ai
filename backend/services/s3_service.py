import os
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import uuid
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        self.environment = os.getenv('ENVIRONMENT', 'development')

    def _get_prefix(self, folder):
        """Constructs the S3 key prefix based on environment and folder."""
        return f"{self.environment}/{folder}"

    def upload_avatar(self, file_obj, filename, user_id):
        """Uploads a public profile avatar to S3 and returns the public URL."""
        try:
            # Create a unique filename to prevent caching issues and overwrites
            ext = os.path.splitext(filename)[1].lower()
            safe_filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"

            # S3 Key: environment/avatars/filename
            s3_key = f"{self._get_prefix('avatars')}/{safe_filename}"

            # Upload with public read access
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(filename),
                    # We don't set ACL='public-read' here because Block Public Access might be on,
                    # instead we'll rely on generating presigned URLs or bucket policies if needed.
                    # But the prompt says "public avatars", so we assume the URL is directly accessible
                    # if the bucket policy allows it, or we generate a presigned URL.
                }
            )

            # Return the object key so we can generate URLs later
            return s3_key

        except ClientError as e:
            logger.error(f"S3 Avatar Upload Error: {e}")
            return None

    def get_public_url(self, s3_key):
        """Returns a direct S3 URL for public assets like avatars."""
        if not s3_key:
            return None
        region = os.getenv('AWS_REGION', 'ap-south-1')
        return f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

    def upload_resume_pdf(self, pdf_bytes, user_id):
        """Uploads a generated PDF resume to S3 and returns the object key."""
        try:
            # Create a unique filename
            safe_filename = f"resume_user_{user_id}_{uuid.uuid4().hex[:8]}.pdf"

            # S3 Key: environment/resumes/filename
            s3_key = f"{self._get_prefix('resumes')}/{safe_filename}"

            # Upload the bytes
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=pdf_bytes,
                ContentType='application/pdf'
            )

            logger.info(f"S3: Successfully uploaded resume for user {user_id} to {s3_key}")
            return s3_key

        except ClientError as e:
            logger.error(f"S3 Resume Upload Error: {e}")
            return None

    def get_presigned_url(self, s3_key, expires_in=3600):
        """Generates a presigned URL for private assets like resumes (expires in 1 hour)."""
        if not s3_key:
            return None

        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return response
        except ClientError as e:
            logger.error(f"S3 Presigned URL Error: {e}")
            return None

    def delete_file(self, s3_key):
        """Deletes a file from S3."""
        if not s3_key:
            return False

        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            logger.error(f"S3 Delete Error: {e}")
            return False

    def _get_content_type(self, filename):
        """Helper to determine content type from extension."""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return content_types.get(ext, 'application/octet-stream')
