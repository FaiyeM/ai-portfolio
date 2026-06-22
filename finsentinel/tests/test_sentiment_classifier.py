"""Tests for nlp/sentiment_classifier.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from nlp.sentiment_classifier import sentiment_from_precomputed, LABEL_MAP


class TestSentimentFromPrecomputed:
    """Tests for the demo-mode sentiment function (no model download needed)."""

    def test_positive_score_returns_positive_label(self):
        result = sentiment_from_precomputed(0.85)
        assert result["label"] == "positive"

    def test_negative_score_returns_negative_label(self):
        result = sentiment_from_precomputed(-0.75)
        assert result["label"] == "negative"

    def test_near_zero_returns_neutral(self):
        result = sentiment_from_precomputed(0.1)
        assert result["label"] == "neutral"

    def test_negative_boundary_returns_neutral(self):
        result = sentiment_from_precomputed(-0.15)
        assert result["label"] == "neutral"

    def test_result_contains_required_keys(self):
        result = sentiment_from_precomputed(0.5)
        assert "label" in result
        assert "sentiment_score" in result
        assert "confidence" in result
        assert "raw_label" in result

    def test_sentiment_score_preserved(self):
        result = sentiment_from_precomputed(0.6)
        assert result["sentiment_score"] == pytest.approx(0.6, abs=1e-4)

    def test_high_negative_score(self):
        result = sentiment_from_precomputed(-0.95)
        assert result["label"] == "negative"
        assert result["confidence"] == pytest.approx(0.95, abs=1e-4)

    def test_label_map_coverage(self):
        """All LABEL_MAP keys should map to numeric values."""
        assert set(LABEL_MAP.keys()) == {"positive", "negative", "neutral"}
        assert LABEL_MAP["positive"] == 1.0
        assert LABEL_MAP["negative"] == -1.0
        assert LABEL_MAP["neutral"] == 0.0
