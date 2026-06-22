"""Zero-shot topic classification using facebook/bart-large-mnli.

Labels: earnings, regulatory action, macroeconomic, fraud allegation, merger acquisition
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

TOPIC_LABELS = [
    "earnings",
    "regulatory action",
    "macroeconomic",
    "fraud allegation",
    "merger acquisition",
]

# Keyword fallback for demo/offline mode
KEYWORD_TOPIC_MAP = {
    "earnings": ["earnings", "revenue", "profit", "quarterly", "eps", "beats", "misses", "guidance", "dividend"],
    "regulatory action": ["regulatory", "investigation", "probe", "asic", "sec", "fine", "penalty", "compliance", "enforcement"],
    "macroeconomic": ["fed", "rate", "inflation", "gdp", "central bank", "monetary", "fiscal", "recession", "macro"],
    "fraud allegation": ["fraud", "misconduct", "misleading", "class action", "lawsuit", "scandal", "governance", "disclosure"],
    "merger acquisition": ["merger", "acquisition", "takeover", "deal", "buyout", "strategic", "combine", "m&a"],
}


@lru_cache(maxsize=1)
def _get_pipeline():
    from transformers import pipeline
    print("  [ZSC] Loading facebook/bart-large-mnli (first run downloads ~1.6GB)...")
    pipe = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1,  # CPU
    )
    print("  [ZSC] Model loaded.")
    return pipe


def classify_topic_live(text: str) -> dict[str, Any]:
    """Classify topic using zero-shot classifier (requires model download)."""
    pipe = _get_pipeline()
    result = pipe(text[:512], candidate_labels=TOPIC_LABELS, multi_label=False)
    top_label = result["labels"][0]
    top_score = result["scores"][0]

    return {
        "topic": top_label,
        "confidence": round(float(top_score), 4),
        "all_scores": {l: round(float(s), 4) for l, s in zip(result["labels"], result["scores"])},
    }


def classify_topic_keywords(text: str, article_type: str | None = None) -> dict[str, Any]:
    """Keyword-based topic classification (fast, no model download)."""
    # Use pre-set article_type if available from sample data
    if article_type:
        type_map = {
            "earnings": "earnings",
            "regulatory": "regulatory action",
            "fraud": "fraud allegation",
            "macro": "macroeconomic",
            "merger": "merger acquisition",
        }
        mapped = type_map.get(article_type, "earnings")
        return {"topic": mapped, "confidence": 0.85, "all_scores": {mapped: 0.85}}

    text_lower = text.lower()
    scores = {}
    for topic, keywords in KEYWORD_TOPIC_MAP.items():
        score = sum(1 for kw in keywords if kw in text_lower) / len(keywords)
        scores[topic] = round(score, 4)

    best_topic = max(scores, key=scores.get)
    return {
        "topic": best_topic,
        "confidence": scores[best_topic],
        "all_scores": scores,
    }
