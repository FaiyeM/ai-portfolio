"""Batch evaluation of ComplianceRAG retrieval quality.

Computes Precision@k and framework attribution accuracy against eval_questions.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EVAL_QUESTIONS_PATH = Path(__file__).parent / "eval_questions.json"


def load_eval_questions() -> list[dict[str, Any]]:
    with open(EVAL_QUESTIONS_PATH) as f:
        return json.load(f)


def precision_at_k(retrieved_chunks: list[dict], expected_keywords: list[str], k: int = 5) -> float:
    """Calculate Precision@k based on keyword overlap in retrieved chunks.

    A chunk is considered relevant if it contains at least one expected keyword.
    """
    top_k = retrieved_chunks[:k]
    if not top_k:
        return 0.0

    relevant_count = 0
    for chunk in top_k:
        chunk_text = chunk.get("text", "").lower()
        if any(kw.lower() in chunk_text for kw in expected_keywords):
            relevant_count += 1

    return relevant_count / len(top_k)


def framework_accuracy(retrieved_chunks: list[dict], expected_framework: str) -> float:
    """Calculate the fraction of top-5 retrieved chunks from the correct framework."""
    top_5 = retrieved_chunks[:5]
    if not top_5:
        return 0.0
    correct = sum(1 for c in top_5 if c.get("framework", "") == expected_framework)
    return correct / len(top_5)


def run_batch_eval(index, metadata: list[dict], k: int = 5) -> dict[str, Any]:
    """Run batch evaluation against all eval questions.

    Returns a summary dict with per-question results and aggregate metrics.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from rag.retriever import retrieve

    questions = load_eval_questions()
    results = []

    for q in questions:
        chunks = retrieve(
            query=q["question"],
            index=index,
            metadata=metadata,
            top_k=k,
            framework_filter=q.get("framework"),
        )
        prec = precision_at_k(chunks, q["expected_keywords"], k)
        fw_acc = framework_accuracy(chunks, q["expected_framework"])

        results.append({
            "id": q["id"],
            "question": q["question"],
            "framework": q["framework"],
            "precision_at_k": round(prec, 3),
            "framework_accuracy": round(fw_acc, 3),
            "top_chunk_framework": chunks[0].get("framework", "None") if chunks else "None",
        })

    avg_precision = sum(r["precision_at_k"] for r in results) / len(results)
    avg_fw_acc = sum(r["framework_accuracy"] for r in results) / len(results)

    return {
        "k": k,
        "total_questions": len(results),
        "mean_precision_at_k": round(avg_precision, 3),
        "mean_framework_accuracy": round(avg_fw_acc, 3),
        "per_question": results,
    }


def print_eval_report(eval_results: dict[str, Any]) -> None:
    """Print a formatted evaluation report."""
    print("\n" + "=" * 60)
    print(f"ComplianceRAG Retrieval Evaluation Report")
    print("=" * 60)
    print(f"Questions evaluated:      {eval_results['total_questions']}")
    print(f"Precision@{eval_results['k']}:           {eval_results['mean_precision_at_k']:.1%}")
    print(f"Framework accuracy:       {eval_results['mean_framework_accuracy']:.1%}")
    print()
    print(f"{'ID':<8} {'Framework':<16} {'P@K':<8} {'FW_Acc':<10} {'Top Chunk Framework'}")
    print("-" * 70)
    for r in eval_results["per_question"]:
        print(
            f"{r['id']:<8} {r['framework']:<16} "
            f"{r['precision_at_k']:.2f}    {r['framework_accuracy']:.2f}      "
            f"{r['top_chunk_framework']}"
        )
    print("=" * 60)
