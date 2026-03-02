import os
from sentence_transformers import SentenceTransformer
from models import db
from models.job import Job
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Initialize the model globally so it's only loaded once in memory
_model = None

def get_model():
    """Lazy load the sentence transformer model to save memory if unused."""
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully.")
    return _model

def generate_embedding(text):
    """
    Generate a vector embedding for the given text.
    Returns a flat list of floats representing the vector.
    """
    if not text or not isinstance(text, str):
        return []

    model = get_model()
    # encode() returns a numpy array, we convert to list for storage/API simplicity
    vector = model.encode(text).tolist()
    return vector

def store_job_embedding(job_id, title, description):
    """
    Generate and store an embedding for a job into PostgreSQL pgvector directly.
    """
    try:
        # Create a rich text block combining title and description
        text_to_embed = f"Job Title: {title}\n\nDescription: {description}"

        # Generate the vector
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
        # Create a rich text block representing the student's semantic identity
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
    Given a student's profile vector, query PostgreSQL using pgvector <=> operator for the closest matching jobs.
    Returns a list of dicts with job_id and similarity_score.
    """
    if not student_vector:
        return []

    try:
        # pgvector cosine distance operator is `<=>`
        # Using pure SQLAlchemy pgvector syntax -> Job.embedding.cosine_distance()
        # similarity = 1 - distance
        
        results = db.session.query(
            Job.job_id,
            Job.embedding.cosine_distance(student_vector).label('distance')
        ).filter(Job.embedding.isnot(None)).order_by('distance').limit(limit * 2).all()

        matches = []
        for r in results:
            # We map 0-2 (cosine distance) to 0-100 similarity points
            distance = float(r.distance) if r.distance is not None else 1.0
            similarity_score = (1.0 - distance) * 100

            # Cap between 0 and 100
            similarity_score = max(0, min(100, similarity_score))

            matches.append({
                'job_id': r.job_id,
                'match_score': round(similarity_score, 1)
            })

        # Sort by match_score descending just to be sure
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:limit]

    except Exception as e:
        logger.error(f"Failed to search for similar jobs: {str(e)}")
        return []
