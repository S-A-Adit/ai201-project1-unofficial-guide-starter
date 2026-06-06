"""Milestone 4 — Embedding + Vector Store.

Loads the chunks produced by chunk.py, embeds them with all-MiniLM-L6-v2, and
stores them in a persistent ChromaDB collection together with source metadata
(source_id, chunk_index, tag, scope) needed for attribution at generation time.

Run:  python embed.py
"""

import json
import os

from sources import BY_ID
from store import get_client, get_collection, get_model, strip_tag, COLLECTION

HERE = os.path.dirname(os.path.abspath(__file__))
CHUNKS_PATH = os.path.join(HERE, "documents", "chunks.jsonl")


def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    if not os.path.exists(CHUNKS_PATH):
        print(f"No chunks at {CHUNKS_PATH}. Run ingest.py -> clean.py -> chunk.py first.")
        return

    records = load_chunks()
    print(f"Loaded {len(records)} chunks.")

    # Embed the body WITHOUT the source tag (the repeated tag is constant noise
    # that shouldn't drive similarity); keep the full tagged text for display.
    bodies = [strip_tag(r["text"], r.get("tag", "")) for r in records]

    model = get_model()
    print(f"Embedding with {model.__class__.__name__} ({len(bodies)} texts)...")
    embeddings = model.encode(bodies, batch_size=64, show_progress_bar=True)

    client = get_client()
    # Reset the collection so re-running doesn't pile up duplicate ids.
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = get_collection(client)

    collection.add(
        ids=[f"{r['source_id']}__{r['chunk_index']}" for r in records],
        embeddings=[e.tolist() for e in embeddings],
        documents=[r["text"] for r in records],
        metadatas=[
            {
                "source_id": r["source_id"],
                "chunk_index": r["chunk_index"],
                "tag": r.get("tag", ""),
                "scope": BY_ID.get(r["source_id"], {}).get("scope", "unknown"),
            }
            for r in records
        ],
    )

    print(f"\nEmbedded {collection.count()} chunks into '{COLLECTION}'.")


if __name__ == "__main__":
    main()
