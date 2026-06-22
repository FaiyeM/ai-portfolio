"""Tests for vendor risk scoring and aggregation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from assessment.aggregator import aggregate_scores
from assessment.domain_weights import DEFAULT_DOMAIN_WEIGHTS, get_weights
from assessment.scorer import load_questionnaire, load_vendor_responses


def test_load_questionnaire_default():
    q = load_questionnaire("default")
    assert "domains" in q
    assert len(q["domains"]) > 0


def test_questionnaire_has_questions():
    q = load_questionnaire("default")
    total_q = sum(len(d["questions"]) for d in q["domains"])
    assert total_q >= 10


def test_load_acme_responses():
    data = load_vendor_responses("Acme Corp")
    assert data["vendor_name"] == "Acme Corp"
    assert "responses" in data
    assert len(data["responses"]) >= 10


def test_load_finco_responses():
    data = load_vendor_responses("FinCo Services")
    assert data["vendor_name"] == "FinCo Services"
    assert "responses" in data


def test_aggregate_scores_returns_required_keys():
    mock_scored = [
        {"domain": "Data Security & Privacy", "question_id": 1, "score": 8, "rationale": "Good", "risk_flags": []},
        {"domain": "Incident Response", "question_id": 2, "score": 5, "rationale": "Average", "risk_flags": ["No IRP test"]},
    ]
    result = aggregate_scores(mock_scored, DEFAULT_DOMAIN_WEIGHTS)
    for key in ["overall_score", "risk_tier", "domain_scores", "top_findings", "questions_scored"]:
        assert key in result


def test_aggregate_score_within_bounds():
    mock_scored = [
        {"domain": "Data Security & Privacy", "question_id": i, "score": s, "rationale": "Test", "risk_flags": []}
        for i, s in enumerate([7, 8, 9, 3, 2], 1)
    ]
    result = aggregate_scores(mock_scored, DEFAULT_DOMAIN_WEIGHTS)
    assert 0.0 <= result["overall_score"] <= 100.0


def test_risk_tier_critical_for_low_scores():
    mock_scored = [
        {"domain": d, "question_id": i, "score": 1, "rationale": "Test", "risk_flags": []}
        for i, d in enumerate(["Data Security & Privacy", "Incident Response", "Business Continuity & DR"], 1)
    ]
    result = aggregate_scores(mock_scored, DEFAULT_DOMAIN_WEIGHTS)
    assert result["risk_tier"] in ("CRITICAL", "HIGH")


def test_risk_tier_low_for_high_scores():
    mock_scored = [
        {"domain": d, "question_id": i, "score": 9, "rationale": "Excellent", "risk_flags": []}
        for i, d in enumerate(DEFAULT_DOMAIN_WEIGHTS.keys(), 1)
    ]
    result = aggregate_scores(mock_scored, DEFAULT_DOMAIN_WEIGHTS)
    assert result["risk_tier"] in ("LOW", "MEDIUM")


def test_domain_weights_sum_to_one():
    total = sum(DEFAULT_DOMAIN_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001


if __name__ == "__main__":
    tests = [
        test_load_questionnaire_default,
        test_questionnaire_has_questions,
        test_load_acme_responses,
        test_load_finco_responses,
        test_aggregate_scores_returns_required_keys,
        test_aggregate_score_within_bounds,
        test_risk_tier_critical_for_low_scores,
        test_risk_tier_low_for_high_scores,
        test_domain_weights_sum_to_one,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
