"""FAISS vector store — build, persist, and load index."""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FAISS_INDEX_PATH
from rag.embedder import embed_texts

INDEX_FILE = "compliance.index"
META_FILE = "compliance_meta.pkl"


def build_index(chunks: list[dict[str, Any]]) -> tuple[Any, list[dict]]:
    """Build a FAISS index from document chunks.

    Returns:
        (faiss_index, metadata_list)
    """
    import faiss

    texts = [c["text"] for c in chunks]
    print(f"  [FAISS] Embedding {len(texts)} chunks...")
    embeddings = embed_texts(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine sim with normalized vecs)
    index.add(embeddings)

    print(f"  [FAISS] Built index with {index.ntotal} vectors (dim={dim}).")
    return index, chunks


def save_index(index, metadata: list[dict], path: str = FAISS_INDEX_PATH) -> None:
    """Persist FAISS index and metadata to disk."""
    import faiss

    save_dir = Path(path)
    save_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(save_dir / INDEX_FILE))
    with open(save_dir / META_FILE, "wb") as f:
        pickle.dump(metadata, f)
    print(f"  [FAISS] Saved index to {save_dir}.")


def load_index(path: str = FAISS_INDEX_PATH) -> tuple[Any, list[dict]] | tuple[None, None]:
    """Load FAISS index and metadata from disk. Returns (None, None) if not found."""
    import faiss

    save_dir = Path(path)
    idx_path = save_dir / INDEX_FILE
    meta_path = save_dir / META_FILE

    if not idx_path.exists() or not meta_path.exists():
        return None, None

    index = faiss.read_index(str(idx_path))
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)

    print(f"  [FAISS] Loaded index with {index.ntotal} vectors.")
    return index, metadata


def get_or_build_index(chunks: list[dict[str, Any]], force_rebuild: bool = False):
    """Load existing index or build a new one from chunks."""
    if not force_rebuild:
        index, metadata = load_index()
        if index is not None:
            return index, metadata

    index, metadata = build_index(chunks)
    save_index(index, metadata)
    return index, metadata
