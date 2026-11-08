import os, json
from pathlib import Path
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")

chunks = json.loads(Path("data/chunks.json").read_text(encoding="utf-8"))
matrix = np.load("data/embeddings.npy")
matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)  # make every arrow length 1

def search(question, top_k=3):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    q = np.array(result.embeddings[0].values, dtype=np.float32)
    q = q / np.linalg.norm(q)
    scores = matrix @ q                      # cosine similarity with every chunk
    best = np.argsort(scores)[::-1][:top_k]  # indexes of the highest scores
    return [(chunks[i], float(scores[i])) for i in best]

if __name__ == "__main__":
    while True:
        question = input("\nAsk (or type q to quit): ")
        if question.strip().lower() == "q":
            break
        for chunk, score in search(question):
            print(f"\n[{score:.3f}] {chunk['source']} #{chunk['chunk_id']}")
            print(chunk["text"][:300], "...")