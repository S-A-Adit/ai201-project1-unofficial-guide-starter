"""Shared vector-store helpers (Milestone 4).

Keeps the embedding model, ChromaDB client, and collection config in one place
so embed.py and retrieve.py agree on them — the same role sources.py plays for
ingestion.
"""

import os

# This environment has TensorFlow installed alongside PyTorch, and transformers
# eagerly probes its TF backend (which fails on Keras 3). We only need PyTorch,
# so disable the TF/Flax backends before sentence-transformers imports them.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "unofficial_guide"
CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

_model = None


def get_model():
    """Load the embedding model once and reuse it (it's a few hundred MB)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def get_client():
    import chromadb
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection(client):
    """Get/create the collection configured for COSINE distance.

    Chroma defaults to squared-L2; cosine puts distances on the ~0-1 scale that
    our relevance thresholds (0.6-0.7 = weak match) assume.
    """
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def strip_tag(text, tag):
    """Remove the leading "[Source - scope] " tag so it doesn't add constant
    noise to the embedding. The full tagged text is still stored for display."""
    if tag and text.startswith(tag):
        return text[len(tag):].strip()
    return text
