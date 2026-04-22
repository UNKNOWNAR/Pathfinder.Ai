"""
Storage Service — Supabase Edition
=====================================
AWS S3 has been replaced with Supabase Storage (free 1GB, no credit card).

Buckets:
  - avatars  (public)  → profile pictures
  - resumes  (private) → generated PDF resumes (signed URLs)

Setup:
1. Create project at supabase.com
2. Create two buckets: 'avatars' (public) and 'resumes' (private)
3. Set env vars: SUPABASE_URL and SUPABASE_SERVICE_KEY
"""
import os
import uuid
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')

def _get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class S3Service:
    """Storage service backed by Supabase. Interface is identical to the old S3Service."""

    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')

    def _get_prefix(self, folder):
        return f"{self.environment}/{folder}"

    def upload_avatar(self, file_obj, filename, user_id):
        """Uploads a profile avatar to Supabase Storage and returns the object path."""
        try:
            ext = os.path.splitext(filename)[1].lower()
            safe_filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
            path = f"{self._get_prefix('avatars')}/{safe_filename}"
            content_type = self._get_content_type(filename)

            file_bytes = file_obj.read()
            client = _get_client()
            client.storage.from_('avatars').upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            return path
        except Exception as e:
            logger.error(f"Supabase avatar upload error: {e}")
            return None

    def get_public_url(self, path):
        """Returns a permanent public URL for avatars bucket."""
        if not path:
            return None
        try:
            client = _get_client()
            return client.storage.from_('avatars').get_public_url(path)
        except Exception as e:
            logger.error(f"Supabase public URL error: {e}")
            return None

    def upload_resume_pdf(self, pdf_bytes, user_id):
        """Uploads a generated PDF resume to Supabase and returns the object path."""
        try:
            safe_filename = f"resume_user_{user_id}_{uuid.uuid4().hex[:8]}.pdf"
            path = f"{self._get_prefix('resumes')}/{safe_filename}"

            client = _get_client()
            client.storage.from_('resumes').upload(
                path=path,
                file=pdf_bytes,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
            return path
        except Exception as e:
            logger.error(f"Supabase resume upload error: {e}")
            return None

    def get_presigned_url(self, path, expires_in=3600):
        """Returns a signed URL for private resume access (expires in 1 hour)."""
        if not path:
            return None
        try:
            client = _get_client()
            result = client.storage.from_('resumes').create_signed_url(path, expires_in)
            return result.get('signedURL') or result.get('signed_url')
        except Exception as e:
            logger.error(f"Supabase signed URL error: {e}")
            return None

    def delete_file(self, path):
        """Deletes a file from its respective bucket."""
        if not path:
            return False
        try:
            client = _get_client()
            bucket = 'resumes' if '/resumes/' in path else 'avatars'
            client.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            logger.error(f"Supabase delete error: {e}")
            return False

    def _get_content_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
        }.get(ext, 'application/octet-stream')
