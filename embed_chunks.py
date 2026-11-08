import os, time, json
from pathlib import Path
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "gemini-embedding-001")
BATCH = 20  # send 20 chunks per request to stay within free limits

chunks = json.loads(Path("data/chunks.json").read_text(encoding="utf-8"))
texts = [c["text"] for c in chunks]
vectors = []

for i in range(0, len(texts), BATCH):
    batch = texts[i:i + BATCH]
    for attempt in range(5):
        try:
            result = client.models.embed_content(
                model=EMBED_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            break
        except Exception as e:
            print("Error, retrying in 20s:", str(e)[:150])
            time.sleep(20)
    else:
        raise SystemExit("Gave up after 5 tries")
    vectors += [e.values for e in result.embeddings]
    print(f"Embedded {len(vectors)}/{len(texts)}")
    time.sleep(2)

np.save("data/embeddings.npy", np.array(vectors, dtype=np.float32))
print("Saved. Vector size:", len(vectors[0]))