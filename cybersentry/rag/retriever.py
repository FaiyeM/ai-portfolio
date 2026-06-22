"""Threat context retriever — queries ChromaDB for relevant threat intelligence."""
from __future__ import annotations

from typing import Any

import chromadb


def retrieve_threat_context(
    collection: chromadb.Collection,
    cve: dict[str, Any],
    n_results: int = 3,
) -> list[dict[str, str]]:
    """Retrieve relevant threat advisory context for a given CVE.

    Constructs a query from the CVE description and keywords, then
    fetches the top-k most semantically similar document sections.
    """
    query_text = (
        cve.get("description", "")
        + " "
        + " ".join(cve.get("keywords", []))
        + " "
        + " ".join(cve.get("affected_products", []))
    )

    if collection.count() == 0:
        return [{"source": "no_docs", "text": "No threat advisories indexed.", "advisory_id": "N/A"}]

    results = collection.query(
        query_texts=[query_text[:1000]],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    contexts = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        contexts.append({
            "source": meta.get("source", "unknown"),
            "advisory_id": meta.get("advisory_id", "N/A"),
            "text": doc,
            "similarity_score": round(1.0 - dist, 3),
        })

    return contexts


def format_context_for_prompt(contexts: list[dict[str, str]]) -> str:
    """Format retrieved contexts into a prompt-ready string."""
    if not contexts:
        return "No relevant threat intelligence found."

    parts = []
    for ctx in contexts:
        parts.append(
            f"[Source: {ctx['source']} | Relevance: {ctx.get('similarity_score', 'N/A')}]\n{ctx['text']}"
        )
    return "\n\n---\n\n".join(parts)
