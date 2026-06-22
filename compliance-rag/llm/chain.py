"""RAG chain: retrieve → augment prompt → generate answer."""
from __future__ import annotations

from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from llm.prompts import SYSTEM_PROMPT, QA_PROMPT, DEMO_ANSWERS
from rag.retriever import format_context


def answer_question(
    question: str,
    chunks: list[dict[str, Any]],
    demo_mode: bool = True,
) -> dict[str, Any]:
    """Run the RAG chain to answer a compliance question.

    Returns:
        dict with 'answer', 'source_chunks', 'confidence_notes', 'demo_mode'
    """
    context = format_context(chunks)

    if demo_mode:
        answer = _demo_answer(question, chunks)
    else:
        answer = _live_answer(question, context)

    return {
        "answer": answer,
        "source_chunks": chunks,
        "confidence_notes": _extract_confidence(answer),
        "demo_mode": demo_mode,
        "context_used": context,
    }


def _demo_answer(question: str, chunks: list[dict]) -> str:
    """Return a canned answer for demo mode, or synthesise from chunks."""
    q_lower = question.lower()

    # Try to match a canned demo answer
    for _key, demo in DEMO_ANSWERS.items():
        if any(kw in q_lower for kw in demo["question_keywords"]):
            return demo["answer"]

    # Fallback: summarise the top chunk content
    if chunks:
        top_chunk = chunks[0]
        return (
            f"**Answer (Demo Mode):** Based on {top_chunk.get('framework', 'the regulatory document')}, "
            f"the following is relevant to your question:\n\n"
            f"{top_chunk['text'][:600]}...\n\n"
            f"**Citation:** {top_chunk.get('framework', 'Unknown')} — {top_chunk.get('source', 'N/A')}\n\n"
            f"**Confidence:** MEDIUM — Demo mode with keyword-matched content. "
            f"Enable live mode for LLM-synthesised answers."
        )

    return (
        "**Answer (Demo Mode):** No relevant regulatory content found for this question. "
        "Please check that the regulatory documents are loaded and try rephrasing your question."
    )


def _live_answer(question: str, context: str) -> str:
    """Call Anthropic API for a live answer."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = QA_PROMPT.format(question=question, context=context[:3000])

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _extract_confidence(answer: str) -> str:
    """Extract confidence level from answer text."""
    answer_upper = answer.upper()
    if "CONFIDENCE: HIGH" in answer_upper:
        return "HIGH"
    elif "CONFIDENCE: MEDIUM" in answer_upper:
        return "MEDIUM"
    elif "CONFIDENCE: LOW" in answer_upper:
        return "LOW"
    return "UNKNOWN"
