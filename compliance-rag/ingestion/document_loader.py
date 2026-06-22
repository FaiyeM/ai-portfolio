"""Document loader and chunker for regulatory documents."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import REGULATORY_DOCS_PATH

FRAMEWORK_FILE_MAP = {
    "APRA CPS 234": "apra_cps234_summary.md",
    "ISO 27001": "iso27001_controls.md",
    "SOC 2": "soc2_trust_criteria.md",
}


def load_documents(framework_filter: str | None = None) -> list[dict[str, Any]]:
    """Load and chunk regulatory documents.

    Args:
        framework_filter: If provided, only load docs for this framework.
                         Use None or "All" to load all frameworks.

    Returns:
        List of chunk dicts with 'text', 'source', 'framework', 'chunk_id' keys.
    """
    chunks = []

    files_to_load = {}
    if framework_filter and framework_filter != "All":
        filename = FRAMEWORK_FILE_MAP.get(framework_filter)
        if filename:
            files_to_load[framework_filter] = REGULATORY_DOCS_PATH / filename
    else:
        for framework, filename in FRAMEWORK_FILE_MAP.items():
            files_to_load[framework] = REGULATORY_DOCS_PATH / filename

    for framework, path in files_to_load.items():
        if not path.exists():
            print(f"  Warning: {path} not found, skipping.")
            continue

        text = path.read_text(encoding="utf-8")
        doc_chunks = _chunk_markdown(text, framework, path.name)
        chunks.extend(doc_chunks)

    return chunks


def _chunk_markdown(text: str, framework: str, source: str) -> list[dict[str, Any]]:
    """Split a markdown document into chunks by section headings."""
    # Split on ## or ### headings
    sections = re.split(r'\n(?=#{1,3} )', text)
    chunks = []

    for i, section in enumerate(sections):
        section = section.strip()
        if len(section) < 50:
            continue

        # Further split long sections into ~400-word chunks
        words = section.split()
        if len(words) > 400:
            sub_chunks = _split_words(section, 400)
        else:
            sub_chunks = [section]

        for j, chunk in enumerate(sub_chunks):
            chunks.append({
                "text": chunk,
                "source": source,
                "framework": framework,
                "chunk_id": f"{source}_s{i}_c{j}",
                "word_count": len(chunk.split()),
            })

    return chunks


def _split_words(text: str, max_words: int) -> list[str]:
    """Split text into chunks of approximately max_words words with 50-word overlap."""
    words = text.split()
    chunks = []
    overlap = 50

    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_words - overlap

    return chunks
