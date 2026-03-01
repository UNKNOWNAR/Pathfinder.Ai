# Migration Notes: Local ChromaDB to AWS RDS pgvector

Currently, the semantic matching engine uses ChromaDB as a local vector store for development. When deploying to AWS, we will migrate to PostgreSQL with the `pgvector` extension (AWS RDS supports this).

## Required Changes for AWS RDS pgvector

### 1. Database Provisioning
- Provision an AWS RDS PostgreSQL instance (version 15+ recommended).
- Enable the `pgvector` extension on the database:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

### 2. Dependency Updates
- Remove `chromadb` from `requirements.txt`.
- Add `pgvector` to `requirements.txt`.
- (Optional but recommended) Add `psycopg3` or ensure `psycopg2-binary` is compatible.

### 3. Schema Changes (SQLAlchemy Models)
Update our `Job` and `StudentProfile` (or User) models to include vector columns.

Example:
```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

class Job(db.Model):
    # ... existing columns ...
    embedding = Column(Vector(384)) # 384 dimensions for all-MiniLM-L6-v2

class User(db.Model):
    # ... existing columns ...
    profile_embedding = Column(Vector(384))
```

### 4. Embedding Generation (services/embedding.py)
The `get_embedding()` logic using `sentence-transformers` (or a managed API like AWS Bedrock / OpenAI) will remain, but we will no longer use ChromaDB clients or collections.

Instead of:
```python
collection.add(ids=[str(job.id)], embeddings=[vector])
```

We will simply save it to the database using SQLAlchemy:
```python
job.embedding = vector
db.session.commit()
```

### 5. Semantic Search Logic (JobsList API)
In `api/harvest_api.py`, the ChromaDB query will be replaced with an SQLAlchemy query using cosine distance (`<=>`).

Example replacement:
```python
# ChromaDB approach:
# results = collection.query(query_embeddings=[student_vector], n_results=10)

# pgvector approach (Cosine Distance):
similar_jobs = Job.query.order_by(Job.embedding.cosine_distance(student_vector)).limit(10).all()

# Or with a distance threshold filter:
# similar_jobs = Job.query.filter(Job.embedding.cosine_distance(student_vector) < 0.5).all()
```

### Summary
1. The local ChromaDB directory (`backend/chroma_db`) will be ignored/deleted.
2. Vector storage will be unified with the relational data in PostgreSQL.
3. Queries will be performed via SQL (`ORDER BY embedding <=> query_vector`).
