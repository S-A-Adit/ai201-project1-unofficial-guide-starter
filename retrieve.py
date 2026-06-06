"""Milestone 4 — Retrieval.

retrieve(query, k) embeds the query with the same model and returns the top-k
most similar chunks from ChromaDB, each with its source metadata and cosine
distance. Running this file directly tests retrieval on 3 of the 5 evaluation
questions and prints the results for inspection.

Run:  python retrieve.py
"""

from store import get_client, get_collection, get_model, strip_tag

TOP_K = 4  # planning.md -> Retrieval Approach

# 3 of the 5 evaluation questions (diverse; each backed by a different source).
TEST_QUERIES = [
    "What makes a financial aid appeal more likely to be approved?",
    "What should I do if my tuition bill is due before financial aid disburses?",
    "How does work-study differ from a regular part-time job for financial aid?",
]


def retrieve(query, k=TOP_K):
    """Return the top-k chunks for a query, best match first."""
    model = get_model()
    collection = get_collection(get_client())

    q_emb = model.encode([query])[0].tolist()
    res = collection.query(query_embeddings=[q_emb], n_results=k)

    # Chroma returns parallel lists wrapped in an outer list (one per query).
    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append(
            {
                "text": doc,
                "source_id": meta["source_id"],
                "chunk_index": meta["chunk_index"],
                "tag": meta["tag"],
                "distance": dist,
            }
        )
    return hits


def main():
    for query in TEST_QUERIES:
        print("=" * 78)
        print(f"QUERY: {query}")
        print("=" * 78)
        for rank, h in enumerate(retrieve(query), 1):
            body = strip_tag(h["text"], h["tag"])
            preview = " ".join(body.split())[:240]
            print(f"\n[{rank}] {h['source_id']} #{h['chunk_index']}  "
                  f"distance={h['distance']:.3f}")
            print(f"    {preview}...")
        print()


if __name__ == "__main__":
    main()
