"""FinBERT-based financial sentiment classifier.

Model: ProsusAI/finbert (downloads ~440MB on first run, cached in ~/.cache/huggingface)
Labels: positive, negative, neutral
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any


LABEL_MAP = {"positive": 1.0, "negative": -1.0, "neutral": 0.0}
SCORE_MAP = {"positive": 1, "negative": -1, "neutral": 0}


@lru_cache(maxsize=1)
def _get_pipeline():
    """Load FinBERT pipeline (cached)."""
    from transformers import pipeline
    print("  [FinBERT] Loading ProsusAI/finbert (first run downloads ~440MB)...")
    pipe = pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        tokenizer="ProsusAI/finbert",
        truncation=True,
        max_length=512,
    )
    print("  [FinBERT] Model loaded.")
    return pipe


def classify_sentiment(text: str) -> dict[str, Any]:
    """Classify financial sentiment of a text snippet.

    Returns:
        dict with 'label' (positive/negative/neutral), 'score' (0-1 confidence),
        'sentiment_score' (-1 to 1), 'raw_label'
    """
    pipe = _get_pipeline()
    result = pipe(text[:512])[0]  # Truncate to avoid BERT limit
    label = result["label"].lower()
    confidence = float(result["score"])
    sentiment_score = LABEL_MAP.get(label, 0.0) * confidence

    return {
        "raw_label": label,
        "label": label,
        "confidence": round(confidence, 4),
        "sentiment_score": round(sentiment_score, 4),
    }


def classify_batch(texts: list[str], batch_size: int = 16) -> list[dict[str, Any]]:
    """Classify sentiment for a batch of texts."""
    pipe = _get_pipeline()
    # Truncate each text
    truncated = [t[:512] for t in texts]
    results = pipe(truncated, batch_size=batch_size)

    output = []
    for r in results:
        label = r["label"].lower()
        confidence = float(r["score"])
        output.append({
            "raw_label": label,
            "label": label,
            "confidence": round(confidence, 4),
            "sentiment_score": round(LABEL_MAP.get(label, 0.0) * confidence, 4),
        })
    return output


def sentiment_from_precomputed(simulated_sentiment: float) -> dict[str, Any]:
    """Use pre-computed sentiment score from sample data (demo mode without GPU)."""
    score = float(simulated_sentiment)
    if score > 0.2:
        label = "positive"
    elif score < -0.2:
        label = "negative"
    else:
        label = "neutral"
    return {
        "raw_label": label,
        "label": label,
        "confidence": round(abs(score), 4),
        "sentiment_score": round(score, 4),
    }
