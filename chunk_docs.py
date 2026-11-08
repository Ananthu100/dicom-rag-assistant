import json
from pathlib import Path

CHUNK_WORDS = 200
OVERLAP_WORDS = 40

def chunk_text(text):
    words = text.split()
    step = CHUNK_WORDS - OVERLAP_WORDS
    for start in range(0, len(words), step):
        piece = words[start:start + CHUNK_WORDS]
        if len(piece) > 30:  
            yield " ".join(piece)

chunks = []
for path in sorted(Path("data/raw").glob("*.txt")):
    if path.stem.endswith("index"):   # skip table-of-contents pages
        continue
    text = path.read_text(encoding="utf-8")
    for i, piece in enumerate(chunk_text(text)):
        chunks.append({"source": path.stem, "chunk_id": i, "text": piece})

Path("data/chunks.json").write_text(json.dumps(chunks, indent=2), encoding="utf-8")
print("Total chunks:", len(chunks))
print("Example chunk:\n", chunks[0]["text"][:400])