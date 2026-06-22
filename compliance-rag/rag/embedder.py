"""Sentence-transformers embedding model wrapper."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_model():
    """Load and cache the sentence-transformers model."""
    from sentence_transformers import SentenceTransformer
    print(f"  [Embedder] Loading model '{EMBEDDING_MODEL}' (first run may download ~80MB)...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"  [Embedder] Model loaded. Embedding dim: {model.get_sentence_embedding_dimension()}")
    return model


def embed_texts(texts: list[str], batch_size: int = 64) -> np.ndarray:
    """Embed a list of texts into vectors.

    Returns:
        numpy array of shape (n_texts, embedding_dim), float32
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine similarity via dot product
    )
    return embeddings.astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string."""
    return embed_texts([query])[0]
