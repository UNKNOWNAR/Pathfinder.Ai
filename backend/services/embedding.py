"""
Embedding Service — Jina AI Edition
=====================================
SentenceTransformer (local CPU model) has been replaced with Jina AI's
free embedding API. This removes the ~90MB model download and heavy CPU
usage on the Render free tier.

Free Tier: 1 million tokens/month — more than enough for this project.
Model: jina-embeddings-v3 (1024 dimensions — matches the pgvector column)

Setup:
1. Sign up at https://jina.ai (free, no credit card)
2. Copy your API key from the dashboard
3. Set the env var: JINA_API_KEY=jina_...
"""
import json
import os
import logging
import requests
from models import db
from models.job import Job
from sqlalchemy import text

logger = logging.getLogger(__name__)

JINA_API_KEY = os.getenv('JINA_API_KEY', '')
JINA_ENDPOINT = 'https://api.jina.ai/v1/embeddings'
JINA_MODEL = 'jina-embeddings-v3'


def generate_embeddings(texts):
    """
    Generate 1024-dimension vector embeddings for a list of texts via Jina AI.
    Returns a list of vectors (lists of floats), or [] on failure.
    """
    if not texts or not isinstance(texts, list):
        return []

    if not JINA_API_KEY:
        logger.error("JINA_API_KEY is not set. Cannot generate embeddings.")
        return []

    try:
        response = requests.post(
            JINA_ENDPOINT,
            headers={
                'Authorization': f'Bearer {JINA_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': JINA_MODEL,
                'input': texts,
                'dimensions': 1024,
                'task': 'retrieval.passage',
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return [d['embedding'] for d in data['data']]
        else:
            logger.error(f"Jina batch embedding failed {response.status_code}: {response.text[:200]}")
            return []
    except Exception as e:
        logger.error(f"Jina batch embedding request failed: {e}")
        return []


def store_job_embedding(job_id, title, description):
    """
    Generate and store an embedding for a single job.
    """
    return batch_store_job_embeddings([(job_id, title, description)])


def batch_store_job_embeddings(job_tuples):
    """
    Generate and store embeddings for multiple jobs in a single batch.
    job_tuples: List of (job_id, title, description)
    """
    if not job_tuples:
        return False

    try:
        texts = [f"Job Title: {t}\n\nDescription: {d}" for _, t, d in job_tuples]
        vectors = generate_embeddings(texts)

        if not vectors or len(vectors) != len(job_tuples):
            return False

        for i, (job_id, _, _) in enumerate(job_tuples):
            job = Job.query.get(job_id)
            if job:
                job.embedding = vectors[i]

        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to store batch embeddings: {str(e)}")
        db.session.rollback()
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

        vectors = generate_embeddings([text_to_embed])
        return vectors[0] if vectors else None
    except Exception as e:
        logger.error(f"Failed to generate embedding for student {student_id}: {str(e)}")
        return None


def find_similar_jobs(student_vector, limit=10):
    """
    Given a student's profile vector, query PostgreSQL using pgvector cosine distance.
    Returns a list of dicts with job_id and match_score (0-100).
    """
    if not student_vector:
        return []

    try:
        import numpy as np

        try:
            results = db.session.query(
                Job.job_id,
                Job.embedding.cosine_distance(student_vector).label('distance')
            ).filter(Job.embedding.isnot(None)).order_by('distance').limit(limit * 2).all()
        except Exception:
            db.session.rollback()
            # Fallback: pure Python cosine similarity
            all_jobs = Job.query.filter(Job.embedding.isnot(None)).all()
            student_vec_np = np.array(student_vector)
            norm_student = np.linalg.norm(student_vec_np)
            if norm_student == 0:
                return []

            class MockResult:
                def __init__(self, job_id, distance):
                    self.job_id = job_id
                    self.distance = distance

            results = []
            for j in all_jobs:
                try:
                    job_vec = json.loads(j.embedding) if isinstance(j.embedding, str) else j.embedding
                    job_vec_np = np.array(job_vec)
                    norm_job = np.linalg.norm(job_vec_np)
                    if norm_job == 0:
                        continue
                    similarity = np.dot(student_vec_np, job_vec_np) / (norm_student * norm_job)
                    results.append(MockResult(j.job_id, 1.0 - similarity))
                except Exception:
                    continue
            results.sort(key=lambda r: r.distance)
            results = results[:limit * 2]

        matches = []
        for r in results:
            distance = float(r.distance) if r.distance is not None else 1.0
            score = max(0, min(100, (1.0 - distance) * 100))
            matches.append({'job_id': r.job_id, 'match_score': round(score, 1)})

        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:limit]

    except Exception as e:
        logger.error(f"Failed to search for similar jobs: {str(e)}")
        return []
