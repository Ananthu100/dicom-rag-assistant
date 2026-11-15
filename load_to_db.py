import os, json
from pathlib import Path
import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv

load_dotenv()
chunks = json.loads(Path("data/chunks.json").read_text(encoding="utf-8"))
emb = np.load("data/embeddings.npy")
assert len(chunks) == len(emb), "Chunk count != embedding count. Re-run chunk_docs.py then embed_chunks.py"
dim = emb.shape[1]

with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    conn.execute("DROP TABLE IF EXISTS chunks")
    conn.execute(f"""
        CREATE TABLE chunks (
            id serial PRIMARY KEY,
            source text,
            chunk_id int,
            content text,
            embedding vector({dim})
        )""")
    for c, v in zip(chunks, emb):
        conn.execute(
            "INSERT INTO chunks (source, chunk_id, content, embedding) VALUES (%s, %s, %s, %s)",
            (c["source"], c["chunk_id"], c["text"], v),
        )
    count = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
print(f"Loaded {count} chunks, vector size {dim}")