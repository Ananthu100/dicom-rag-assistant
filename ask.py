import os
from dotenv import load_dotenv
from google import genai
from search import search

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-3.8-flash")

PROMPT = """You are a DICOM assistant. Answer the question using ONLY the context below.
- If the context does not contain the answer, say "I don't have enough information in my documents."
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
    reply = client.models.generate_content(
        model=CHAT_MODEL,
        contents=PROMPT.format(context=context, question=question),
    )
    return reply.text, hits

if __name__ == "__main__":
    while True:
        question = input("\nAsk (or type q to quit): ")
        if question.strip().lower() == "q":
            break
        text, hits = answer(question)
        print("\n" + text)
        print("\nSources used:", ", ".join(f"{c['source']} #{c['chunk_id']}" for c, _ in hits))