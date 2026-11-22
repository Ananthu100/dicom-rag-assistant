import os
from dotenv import load_dotenv
from google import genai
from search_db import search
import time
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-3.8-flash")

FALLBACK_MODEL = os.getenv("FALLBACK_CHAT_MODEL", "gemini-3.5-flash")

def generate_with_retry(prompt):
    for model in [CHAT_MODEL, FALLBACK_MODEL]:
        for attempt in range(3):
            try:
                text = client.models.generate_content(model=model, contents=prompt).text
                print(f"[answered by {model}]")
                return text
            except Exception as e:
                if any(code in str(e) for code in ("503", "429", "UNAVAILABLE")):
                    wait = 5 * (attempt + 1)
                    print(f"{model} is busy, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise  # a real bug, so show it
    raise RuntimeError("All models are busy. Please try again in a few minutes.")

PROMPT = """You are a DICOM assistant. Answer the question using ONLY the context below.
- If the context has nothing relevant, say "I don't have enough information in my documents."
- If the context only partly answers the question, share what it does say, and clearly state what it does not cover.
- Never use outside knowledge and never guess values the context does not state.
- Keep the answer short and clear.
- After each fact, cite its source like [user__ae #1].

CONTEXT:
{context}

QUESTION: {question}
"""

def answer(question, top_k=4):
    hits = search(question, top_k=top_k)
    context = "\n\n".join(
        f"[{chunk['source']} #{chunk['chunk_id']}]\n{chunk['text']}" for chunk, _ in hits
    )
    
    text = generate_with_retry(PROMPT.format(context=context, question=question))
    return text, hits

if __name__ == "__main__":
    while True:
        question = input("\nAsk (or type q to quit): ")
        if question.strip().lower() == "q":
            break
        text, hits = answer(question)
        print("\n" + text)
        print("\nSources used:", ", ".join(f"{c['source']} #{c['chunk_id']}" for c, _ in hits))