"""Top-k retriever with optional framework metadata filtering."""
from __future__ import annotations

from typing import Any

import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TOP_K
from rag.embedder import embed_query


def retrieve(
    query: str,
    index,
    metadata: list[dict[str, Any]],
    top_k: int = TOP_K,
    framework_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve top-k relevant chunks for a query.

    Args:
        query: Natural language question
        index: FAISS index
        metadata: List of chunk metadata dicts matching index order
        top_k: Number of chunks to return
        framework_filter: Optionally restrict to a specific framework

    Returns:
        List of chunk dicts with added 'score' field
    """
    query_vec = embed_query(query).reshape(1, -1)

    # Retrieve more candidates than needed when filtering
    search_k = top_k * 3 if framework_filter and framework_filter != "All" else top_k

    scores, indices = index.search(query_vec, min(search_k, index.ntotal))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        chunk = metadata[idx].copy()
        chunk["score"] = float(score)

        # Apply framework filter
        if framework_filter and framework_filter != "All":
            if chunk.get("framework", "") != framework_filter:
                continue

        results.append(chunk)
        if len(results) >= top_k:
            break

    return results


def format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks into a prompt context string."""
    if not chunks:
        return "No relevant regulatory content found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {chunk.get('framework', 'Unknown')} | "
            f"File: {chunk.get('source', 'unknown')} | "
            f"Relevance: {chunk.get('score', 0):.3f}]\n\n{chunk['text']}"
        )
    return "\n\n" + "─" * 60 + "\n\n".join(parts)
