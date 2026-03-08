import os
import logging
import requests
from models import db
from models.job import Job
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Bedrock Configuration
BEDROCK_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
BEDROCK_API_KEY = os.getenv('BEDROCK_API_KEY', '')

def generate_embedding(text_to_embed):
    """
    Generate a vector embedding using Amazon Titan Embeddings v2 via AWS Bedrock API.
    Returns a flat list of floats representing the vector.
    """
    if not text_to_embed or not isinstance(text_to_embed, str):
        return []

    if not BEDROCK_API_KEY:
        logger.error("BEDROCK_API_KEY is not configured for embeddings.")
        return []

    url = f"https://bedrock-runtime.{BEDROCK_REGION}.amazonaws.com/model/amazon.titan-embed-text-v2:0/invoke"
    headers = {
        "Authorization": f"Bearer {BEDROCK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputText": text_to_embed,
        "dimensions": 1024,
        "normalize": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            # Titan v2 returns 'embedding' array
            return data.get('embedding', [])
        else:
            logger.error(f"Bedrock embedding failed with {response.status_code}: {response.text[:200]}")
            return []
    except Exception as e:
        logger.error(f"Failed to generate embedding via Bedrock: {str(e)}")
        return []

def store_job_embedding(job_id, title, description):
    """
    Generate and store an embedding for a job into PostgreSQL pgvector directly.
    """
    try:
        text_to_embed = f"Job Title: {title}\n\nDescription: {description}"
        vector = generate_embedding(text_to_embed)

        if not vector:
            return False

        job = Job.query.get(job_id)
        if job:
            job.embedding = vector
            db.session.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to store embedding for job {job_id}: {str(e)}")
        return False

def store_student_embedding(student_id, skills, headline, summary):
    """
    Generate an embedding for a student profile based on their skills and experience.
    Returns the vector so it can be saved in the SQL database.
    """
    try:
        text_parts = []
        if headline:
            text_parts.append(f"Headline: {headline}")
        if skills:
            text_parts.append(f"Skills: {skills}")
        if summary:
            text_parts.append(f"Summary: {summary}")

        text_to_embed = "\n\n".join(text_parts)

        if not text_to_embed.strip():
            return None

        return generate_embedding(text_to_embed)
    except Exception as e:
        logger.error(f"Failed to generate embedding for student {student_id}: {str(e)}")
        return None

def find_similar_jobs(student_vector, limit=10):
    """
    Given a student's profile vector, query PostgreSQL using pgvector <=> operator for closest matching jobs.
    Returns a list of dicts with job_id and similarity_score.
    """
    if student_vector is None or len(student_vector) == 0:
        return []

    try:
        # Use PGVector for fast cosine distance matching
        results = db.session.query(
            Job.job_id,
            Job.embedding.cosine_distance(student_vector).label('distance')
        ).filter(
            Job.embedding.isnot(None)
        ).order_by('distance').limit(limit).all()

        matches = []
        for r in results:
            # Map pgvector cosine distance (0-2) to a 0-100 similarity score
            distance = float(r.distance) if r.distance is not None else 1.0
            similarity_score = (1.0 - distance) * 100
            similarity_score = max(0, min(100, similarity_score))

            matches.append({
                'job_id': r.job_id,
                'match_score': round(similarity_score, 1)
            })

        return matches

    except Exception as e:
        logger.error(f"Failed to search for similar jobs: {str(e)}")
        return []
