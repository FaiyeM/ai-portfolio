"""ChromaDB vector store setup and document ingestion."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHROMA_DB_PATH, THREAT_DOCS_PATH

COLLECTION_NAME = "threat_advisories"


def get_client() -> chromadb.Client:
    """Return a persistent ChromaDB client."""
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False),
    )
    return client


def get_or_create_collection(client: chromadb.Client) -> chromadb.Collection:
    """Get or create the threat advisories collection."""
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"  [ChromaDB] Using existing collection '{COLLECTION_NAME}' ({collection.count()} docs).")
    except Exception:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"  [ChromaDB] Created new collection '{COLLECTION_NAME}'.")
    return collection


def ingest_threat_docs(collection: chromadb.Collection, force_reload: bool = False) -> int:
    """Ingest threat advisory markdown files into the vector store."""
    if collection.count() > 0 and not force_reload:
        print(f"  [ChromaDB] Collection already has {collection.count()} documents. Skipping ingestion.")
        return collection.count()

    docs = []
    ids = []
    metadatas = []

    for i, md_file in enumerate(sorted(THREAT_DOCS_PATH.glob("*.md"))):
        text = md_file.read_text(encoding="utf-8")
        # Chunk the document into sections (split by ##)
        sections = [s.strip() for s in text.split("\n## ") if s.strip()]
        for j, section in enumerate(sections):
            doc_id = f"{md_file.stem}_section_{j}"
            docs.append(section[:2000])  # Truncate to avoid embedding limits
            ids.append(doc_id)
            metadatas.append({
                "source": md_file.name,
                "advisory_id": md_file.stem.upper(),
                "section_index": j,
            })

    if docs:
        collection.add(documents=docs, ids=ids, metadatas=metadatas)
        print(f"  [ChromaDB] Ingested {len(docs)} document sections from {THREAT_DOCS_PATH}.")

    return len(docs)
