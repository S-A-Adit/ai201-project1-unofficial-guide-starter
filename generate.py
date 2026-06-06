"""Milestone 5 — Grounded generation.

ask(question) runs the full RAG query path: retrieve -> filter by relevance ->
build a strict grounding prompt -> call Groq (llama-3.3-70b-versatile) ->
return the answer plus a programmatically-built source list.

Grounding is enforced two ways, not merely suggested:
  1. Structural: only chunks within RELEVANCE_CUTOFF cosine distance are passed
     as context. If none qualify (e.g. an off-domain question), we return the
     "not enough information" answer WITHOUT calling the LLM — so it cannot
     invent an answer from training knowledge.
  2. Prompt: the system prompt forbids outside knowledge and pins the exact
     refusal string.

Source attribution is built from the retrieved chunks' metadata (source_id +
URL from sources.py), so it is guaranteed by code rather than trusted to the
model to add.

Run:  python generate.py        (end-to-end test on a few queries)
"""

import os

from dotenv import load_dotenv

from retrieve import retrieve
from sources import BY_ID

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
RELEVANCE_CUTOFF = 0.70  # cosine distance; above this a chunk is too weak to trust
NOT_ENOUGH = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are the Unofficial Guide to financial aid at Ohio State University. "
    "Answer the question using ONLY the information in the numbered context "
    "documents provided in the user's message.\n"
    "Rules:\n"
    "- Use only facts stated in the context. Do NOT use outside or prior knowledge.\n"
    "- Do not speculate, generalize, or fill in gaps.\n"
    f'- If the context does not contain enough information, reply with exactly: "{NOT_ENOUGH}"\n'
    "- Cite the context document numbers you used, like [1] or [2], inline.\n"
    "- Keep the answer concise (a few sentences)."
)

_client = None


def get_client():
    global _client
    if _client is None:
        from groq import Groq
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _source_label(source_id):
    """Human-readable attribution for a source_id, including its URL if known."""
    src = BY_ID.get(source_id, {})
    url = src.get("url")
    tag = src.get("tag", f"[{source_id}]")
    return f"{tag} {source_id}" + (f" — {url}" if url else "")


def ask(question, k=4):
    """Return {"answer": str, "sources": [str], "chunks": [hit]}."""
    hits = retrieve(question, k=k)
    relevant = [h for h in hits if h["distance"] <= RELEVANCE_CUTOFF]

    # No sufficiently-relevant context -> refuse without calling the LLM.
    if not relevant:
        return {"answer": NOT_ENOUGH, "sources": [], "chunks": []}

    # Build numbered context. The number lets the model cite [1]/[2] and lets us
    # map a citation back to a source.
    blocks = []
    for i, h in enumerate(relevant, 1):
        body = h["text"]
        blocks.append(f"[{i}] (source: {h['source_id']})\n{body}")
    context = "\n\n".join(blocks)

    user_msg = (
        f"Context documents:\n{context}\n\n"
        f"Question: {question}"
    )

    resp = get_client().chat.completions.create(
        model=MODEL,
        temperature=0,  # deterministic; minimizes creative drift from context
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    answer = resp.choices[0].message.content.strip()

    # Programmatic source attribution: dedupe by source_id, preserve rank order.
    seen, sources = set(), []
    for h in relevant:
        if h["source_id"] not in seen:
            seen.add(h["source_id"])
            sources.append(_source_label(h["source_id"]))

    # If the model refused, don't imply the sources backed an answer.
    if answer == NOT_ENOUGH:
        sources = []

    return {"answer": answer, "sources": sources, "chunks": relevant}


# ---- End-to-end test harness ----
TEST_QUERIES = [
    "What makes a financial aid appeal more likely to be approved?",
    "What should I do if my tuition bill is due before financial aid disburses?",
    "How does work-study differ from a regular part-time job for financial aid?",
    "What's the best pizza place near campus?",  # off-domain -> should refuse
]


def main():
    for q in TEST_QUERIES:
        print("=" * 78)
        print(f"Q: {q}")
        print("-" * 78)
        result = ask(q)
        print(result["answer"])
        if result["sources"]:
            print("\nRetrieved from:")
            for s in result["sources"]:
                print(f"  • {s}")
        print()


if __name__ == "__main__":
    main()
