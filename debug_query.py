import sys
from search_db import search

for chunk, score in search(" ".join(sys.argv[1:]), top_k=15):
    print(f"{score:.3f}  {chunk['source']} #{chunk['chunk_id']}  {chunk['text'][:120]}")