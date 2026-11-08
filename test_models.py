import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CHAT_MODEL = "gemini-3.8-flash"
EMBED_MODEL = "gemini-embedding-001"

# CHAT MODEL
chat_reply = client.models.generate_content(
    model=CHAT_MODEL,
    contents="In one sentence,What is DICOM?",
)
print("CHAT:",chat_reply.text)

# EMBED MODEL
embedding = client.models.embed_content(
    model=EMBED_MODEL,
    contents="What does C-ECHO do?",
)
vector = embedding.embeddings[0].values
print("Embedding Length:", len(vector))
print("First 5 Numbers:",vector[:5])