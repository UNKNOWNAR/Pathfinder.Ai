import os
from sentence_transformers import SentenceTransformer
import chromadb
import logging

logger = logging.getLogger(__name__)

# Initialize the model globally so it's only loaded once in memory
# all-MiniLM-L6-v2 is a great balance of size (80MB) and performance for semantic matching
_model = None

# Initialize ChromaDB client globally
_chroma_client = None
_job_collection = None

def get_model():
    """Lazy load the sentence transformer model to save memory if unused."""
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
        # Ensure it downloads to a specific cache if needed, but default is fine
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully.")
    return _model

def get_chroma_client():
    """Initialize persistent local ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        # Define the local storage directory for ChromaDB
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chroma_db')
        os.makedirs(db_path, exist_ok=True)

        logger.info(f"Initializing ChromaDB client at {db_path}...")
        _chroma_client = chromadb.PersistentClient(path=db_path)
    return _chroma_client

def get_job_collection():
    """Get or create the ChromaDB collection for jobs."""
    global _job_collection
    if _job_collection is None:
        client = get_chroma_client()
        # Create a collection using cosine similarity
        _job_collection = client.get_or_create_collection(
            name="job_embeddings",
            metadata={"hnsw:space": "cosine"}
        )
    return _job_collection

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
    Generate and store an embedding for a job into ChromaDB.
    Combines title and description for optimal semantic context.
    """
    try:
        # Create a rich text block combining title and description
        text_to_embed = f"Job Title: {title}\n\nDescription: {description}"

        # Generate the vector
        vector = generate_embedding(text_to_embed)

        if not vector:
            return False

        # Add to ChromaDB
        collection = get_job_collection()

        # We store the ID as a string, because ChromaDB requires string IDs
        collection.upsert(
            ids=[str(job_id)],
            embeddings=[vector],
            metadatas=[{"title": title}]  # Minimal metadata, real data stays in PostgreSQL
        )
        return True
    except Exception as e:
        logger.error(f"Failed to store embedding for job {job_id}: {str(e)}")
        return False

def store_student_embedding(student_id, skills, headline, summary):
    """
    Generate an embedding for a student profile based on their skills and experience.
    Returns the vector so it can be saved in the SQL database.
    (Student vectors are stored in PostgreSQL on the Profile table, while Jobs are in ChromaDB)
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
    Given a student's profile vector, query ChromaDB for the closest matching jobs.
    Returns a list of dicts with job_id and similarity_score.
    """
    if not student_vector:
        return []

    try:
        collection = get_job_collection()

        # Check if the collection is empty
        if collection.count() == 0:
            return []

        # We query for more results than we need just in case some jobs were deleted in Postgres
        # but haven't been purged from Chroma yet.
        results = collection.query(
            query_embeddings=[student_vector],
            n_results=min(limit * 2, collection.count())
        )

        # Results format: {'ids': [['1', '2']], 'distances': [[0.1, 0.2]], 'metadatas': [...]}
        matches = []
        if results and 'ids' in results and len(results['ids']) > 0:
            ids = results['ids'][0]
            distances = results['distances'][0]

            for i in range(len(ids)):
                # Convert cosine distance to cosine similarity (0-100% scale)
                # ChromaDB cosine distance: 1 - cosine_similarity
                # So similarity = 1 - distance
                similarity_score = (1.0 - distances[i]) * 100

                # Cap between 0 and 100
                similarity_score = max(0, min(100, similarity_score))

                matches.append({
                    'job_id': int(ids[i]),
                    'match_score': round(similarity_score, 1)
                })

        # Sort by match_score descending just to be sure
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:limit]

    except Exception as e:
        logger.error(f"Failed to search for similar jobs: {str(e)}")
        return []
