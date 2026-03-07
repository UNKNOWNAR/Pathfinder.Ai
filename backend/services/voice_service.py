import boto3
import os
import uuid
import logging
from botocore.exceptions import ClientError
from services.s3_service import S3Service

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        # AWS region for Polly (usually us-east-1 has the most neural voices)
        self.polly_client = boto3.client('polly', region_name='us-east-1')
        self.s3_service = S3Service()
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        self.environment = os.getenv('ENVIRONMENT', 'development')

    def synthesize_speech(self, text, voice_id='Matthew', engine='neural'):
        """
        Converts text to speech using AWS Polly and uploads to S3.
        Returns the S3 Key of the generated audio file.
        """
        try:
            # 1. Synthesize speech
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine
            )

            if 'AudioStream' in response:
                # 2. Generate a unique filename
                filename = f"voice_{uuid.uuid4().hex}.mp3"
                s3_folder = f"{self.environment}/interviews/audio"
                s3_key = f"{s3_folder}/{filename}"

                # 3. Upload the stream directly to S3
                # We use the S3 client directly here since s3_service.upload_avatar 
                # might be too specific (handles fileobj/content_type differently)
                s3_client = boto3.client('s3')
                s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=response['AudioStream'].read(),
                    ContentType='audio/mpeg'
                )

                return s3_key
            
            return None

        except ClientError as e:
            logger.error(f"AWS Polly synthesis failed: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred during voice synthesis: {e}")
            return None

    def get_audio_url(self, s3_key):
        """
        Returns a presigned URL for the audio file.
        """
        if not s3_key:
            return None
        return self.s3_service.get_presigned_url(s3_key, expires_in=3600)
