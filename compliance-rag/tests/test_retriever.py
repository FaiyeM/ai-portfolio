"""Tests for ComplianceRAG retriever and document loader."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.document_loader import load_documents, _chunk_markdown


def test_load_all_documents_returns_chunks():
    chunks = load_documents()
    assert len(chunks) > 0, "Should load at least some chunks"


def test_load_apra_only():
    chunks = load_documents(framework_filter="APRA CPS 234")
    assert all(c["framework"] == "APRA CPS 234" for c in chunks)
    assert len(chunks) > 0


def test_load_iso_only():
    chunks = load_documents(framework_filter="ISO 27001")
    assert all(c["framework"] == "ISO 27001" for c in chunks)
    assert len(chunks) > 0


def test_load_soc2_only():
    chunks = load_documents(framework_filter="SOC 2")
    assert all(c["framework"] == "SOC 2" for c in chunks)
    assert len(chunks) > 0


def test_chunk_has_required_fields():
    chunks = load_documents()
    for chunk in chunks[:5]:
        assert "text" in chunk
        assert "source" in chunk
        assert "framework" in chunk
        assert "chunk_id" in chunk
        assert len(chunk["text"]) > 0


def test_chunk_markdown_splits_by_heading():
    sample = """# Title

## Section One
Content of section one with enough words to form a meaningful chunk here.

## Section Two
Content of section two with enough words to form a meaningful chunk here.
"""
    chunks = _chunk_markdown(sample, "TEST", "test.md")
    assert len(chunks) >= 2


def test_chunk_text_not_empty():
    chunks = load_documents()
    for chunk in chunks:
        assert len(chunk["text"].strip()) > 10, "Chunks should not be empty or near-empty"


if __name__ == "__main__":
    tests = [
        test_load_all_documents_returns_chunks,
        test_load_apra_only,
        test_load_iso_only,
        test_load_soc2_only,
        test_chunk_has_required_fields,
        test_chunk_markdown_splits_by_heading,
        test_chunk_text_not_empty,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
