import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ask import answer

logger = logging.getLogger(__name__)

@csrf_exempt  # simple JSON API for now; we'll revisit before any deployment
@require_POST
def ask_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": 'Send JSON like {"question": "..."}'}, status=400)

    question = (body.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "Question is empty."}, status=400)
    if len(question) > 500:
        return JsonResponse({"error": "Question too long (max 500 characters)."}, status=400)

    try:
        text, hits = answer(question)
    except Exception:
        logger.exception("Answering failed")
        return JsonResponse({"error": "The assistant is busy, please try again shortly."}, status=503)

    sources = [
        {"source": chunk["source"], "chunk_id": chunk["chunk_id"],
         "score": round(score, 3), "snippet": chunk["text"][:200]}
        for chunk, score in hits
    ]
    return JsonResponse({"question": question, "answer": text, "sources": sources})