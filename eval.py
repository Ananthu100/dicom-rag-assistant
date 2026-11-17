import time
from search_db import search

# (question, list of pages that count as a correct answer)
EVAL_SET = [
    ("What is an Application Entity?", ["user__concepts_ae", "user__ae"]),
    ("What are the rules for a valid AE title?", ["user__ae"]),
    ("What is a presentation context?", ["user__presentation_introduction", "user__concepts_contexts"]),
    ("What is an abstract syntax?", ["user__presentation_introduction", "user__concepts_contexts"]),
    ("What is a transfer syntax?", ["user__presentation_introduction", "user__concepts_contexts", "user__presentation_negotiation"]),
    ("How do I request an association with a peer?", ["user__association_requesting", "user__ae_scu"]),
    ("How do I accept incoming associations?", ["user__association_accepting"]),
    ("How do I start an SCP server?", ["user__ae_scp", "user__association_accepting"]),
    ("How do I create an SCU?", ["user__ae_scu"]),
    ("What is a UID in DICOM?", ["user__concepts_uids"]),
    ("What is the DICOM information model?", ["user__concepts_information_model"]),
    ("What is role selection?", ["user__presentation_role_selection"]),
    ("How does presentation context negotiation work?", ["user__presentation_negotiation"]),
    ("How does the acceptor handle presentation contexts?", ["user__presentation_acceptor"]),
    ("How does the requestor propose presentation contexts?", ["user__presentation_requestor"]),
    ("What are event handlers?", ["user__events_handlers"]),
    ("What event types are available?", ["user__events_types"]),
    ("How do I install pynetdicom?", ["user__installation"]),
    ("Can I use private abstract syntaxes?", ["user__presentation_private"]),
    ("What is a DICOM association?", ["user__concepts_association", "user__association_requesting", "user__association_accepting"]),
    ("What does C-ECHO do?", ["service_classes__verification_service_class"]),
    ("How do I check connectivity with a peer using C-ECHO?", ["service_classes__verification_service_class", "user__ae_scu"]),
    ("What does C-FIND do?", ["service_classes__query_retrieve_service_class"]),
    ("What is the difference between C-GET and C-MOVE?", ["service_classes__query_retrieve_service_class"]),
    ("How does C-MOVE send instances to another AE?", ["service_classes__query_retrieve_service_class"]),
    ("What is the query/retrieve information model?", ["service_classes__query_retrieve_service_class", "user__concepts_information_model"]),
    ("What is C-STORE used for?", ["service_classes__storage_service_class"]),
    ("How do I query a modality worklist?", ["service_classes__basic_worklist_service_class"]),
]

hit1 = hit3 = hit5 = 0
reciprocal = 0.0
misses = []

for question, expected in EVAL_SET:
    results = search(question, top_k=5)
    sources = [chunk["source"] for chunk, _ in results]
    rank = next((i + 1 for i, s in enumerate(sources) if s in expected), None)
    print(f"rank={rank}  {question}")
    if rank:
        hit1 += rank <= 1
        hit3 += rank <= 3
        hit5 += rank <= 5
        reciprocal += 1 / rank
    else:
        misses.append((question, expected, sources))
    time.sleep(1)  # stay gentle with the free API limits

n = len(EVAL_SET)
print(f"Questions: {n}")
print(f"Hit@1: {hit1 / n:.0%}")
print(f"Hit@3: {hit3 / n:.0%}")
print(f"Hit@5: {hit5 / n:.0%}")
print(f"MRR:   {reciprocal / n:.2f}")

for question, expected, sources in misses:
    print(f"\nMISS: {question}\n  expected: {expected}\n  got: {sources}")