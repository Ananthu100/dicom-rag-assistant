import os
import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")

def search(question, top_k=3):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    q = np.array(result.embeddings[0].values, dtype=np.float32)

    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        register_vector(conn)
        rows = conn.execute(
            """SELECT source, chunk_id, content, 1 - (embedding <=> %s) AS score
               FROM chunks
               ORDER BY embedding <=> %s
               LIMIT %s""",
            (q, q, top_k),
        ).fetchall()

    return [({"source": r[0], "chunk_id": r[1], "text": r[2]}, float(r[3])) for r in rows]