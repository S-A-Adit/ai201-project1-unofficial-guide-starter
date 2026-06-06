"""Milestone 3 — Chunking.

Splits the cleaned documents in documents/clean/ into overlapping chunks using
the strategy from planning.md:

  * chunk size  = 600 characters (~150 tokens; stays under all-MiniLM-L6-v2's
                  256-token input limit)
  * overlap     = 100 characters (~17%; keeps a fact from being split mid-thought)
  * each chunk is prefixed with its source tag for attribution and to keep
    school-specific vs. general content distinguishable.

The character window snaps to the nearest sentence/space boundary so chunks are
complete thoughts rather than mid-word fragments (planning.md → Chunking Strategy).

Writes documents/chunks.jsonl, prints 5 representative chunks, and reports the
total chunk count.

Run:  python chunk.py
"""

import json
import os

from sources import BY_ID

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR = os.path.join(HERE, "documents", "clean")
CHUNKS_PATH = os.path.join(HERE, "documents", "chunks.jsonl")

CHUNK_SIZE = 600
OVERLAP = 100
# Only snap to a boundary if it lands past this fraction of the window,
# so chunks stay close to the target size instead of collapsing short.
MIN_BOUNDARY = 0.6


def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP, tag=""):
    """Sliding character window with sentence/space boundary snapping."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    n = len(text)
    start = 0
    while start < n:
        end = min(start + size, n)

        # Snap the cut to a clean boundary (don't bother on the final chunk).
        if end < n:
            window = text[start:end]
            cut = -1
            for sep in (". ", ".\n", "? ", "! ", "\n"):
                idx = window.rfind(sep)
                if idx > size * MIN_BOUNDARY:
                    cut = idx + len(sep)
                    break
            if cut == -1:
                idx = window.rfind(" ")
                if idx > size * MIN_BOUNDARY:
                    cut = idx + 1
            if cut != -1:
                end = start + cut

        body = text[start:end].strip()
        if body:
            chunks.append(f"{tag} {body}".strip() if tag else body)

        if end >= n:
            break
        start = max(end - overlap, start + 1)  # overlap; guarantee progress
        # Don't begin the next chunk mid-word: nudge start to the nearest
        # space/newline within the overlap so chunks read as whole thoughts.
        space, newline = text.find(" ", start), text.find("\n", start)
        cands = [c for c in (space, newline) if 0 <= c - start <= overlap]
        if cands:
            start = min(cands) + 1

    return chunks


def build():
    records = []
    per_doc = {}
    for fname in sorted(os.listdir(CLEAN_DIR)):
        if not fname.endswith(".txt"):
            continue
        sid = os.path.splitext(fname)[0]
        tag = BY_ID.get(sid, {}).get("tag", f"[{sid}]")
        with open(os.path.join(CLEAN_DIR, fname), "r", encoding="utf-8") as f:
            text = f.read()

        doc_chunks = chunk_text(text, tag=tag)
        per_doc[sid] = len(doc_chunks)
        for i, ch in enumerate(doc_chunks):
            records.append({"source_id": sid, "tag": tag, "chunk_index": i, "text": ch})
    return records, per_doc


def main():
    if not os.path.isdir(CLEAN_DIR):
        print(f"No cleaned documents at {CLEAN_DIR}. Run ingest.py then clean.py first.")
        return

    records, per_doc = build()

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Per-document breakdown.
    print("Chunks per document:")
    for sid, n in per_doc.items():
        print(f"  {sid:32s} {n:4d}")

    # 5 representative chunks, spread across the corpus so we see different sources.
    print("\n" + "=" * 70)
    print("5 REPRESENTATIVE CHUNKS")
    print("=" * 70)
    if records:
        step = max(len(records) // 5, 1)
        for r in records[::step][:5]:
            print(f"\n--- {r['source_id']} #{r['chunk_index']} "
                  f"({len(r['text'])} chars) ---")
            print(r["text"])

    print("\n" + "=" * 70)
    print(f"TOTAL CHUNKS: {len(records)}  across {len(per_doc)} documents")
    print(f"Saved to {CHUNKS_PATH}")


if __name__ == "__main__":
    main()
