"""Aggregate individual question scores into domain and overall risk scores."""
from __future__ import annotations

from collections import defaultdict
from typing import Any


def aggregate_scores(
    scored_questions: list[dict[str, Any]],
    domain_weights: dict[str, float],
) -> dict[str, Any]:
    """Compute domain-level and overall risk scores.

    Args:
        scored_questions: List of scored question dicts from scorer.py
        domain_weights: Dict mapping domain name to weight (must sum to 1.0)

    Returns:
        Aggregation result with domain_scores, overall_score, risk_tier, top_findings
    """
    # Group scores by domain
    domain_scores_raw: dict[str, list[float]] = defaultdict(list)
    domain_flags: dict[str, list[str]] = defaultdict(list)

    for q in scored_questions:
        domain = q.get("domain", "Unknown")
        domain_scores_raw[domain].append(q.get("score", 0))
        domain_flags[domain].extend(q.get("risk_flags", []))

    # Average score per domain (0-10 scale)
    domain_averages = {
        domain: sum(scores) / len(scores) if scores else 0.0
        for domain, scores in domain_scores_raw.items()
    }

    # Weighted overall score
    overall_score = 0.0
    weighted_domain_scores = {}

    for domain, weight in domain_weights.items():
        avg = domain_averages.get(domain, 0.0)
        weighted_contribution = avg * weight * 10.0  # Scale to 100
        overall_score += weighted_contribution
        weighted_domain_scores[domain] = {
            "raw_average": round(avg, 2),
            "weight": weight,
            "weighted_contribution": round(weighted_contribution, 2),
            "score_out_of_100": round(avg * 10.0, 1),
        }

    overall_score = round(min(100.0, overall_score), 1)

    # Risk tier mapping
    if overall_score >= 80:
        risk_tier = "LOW"
    elif overall_score >= 60:
        risk_tier = "MEDIUM"
    elif overall_score >= 40:
        risk_tier = "HIGH"
    else:
        risk_tier = "CRITICAL"

    # Top risk findings
    all_flags = []
    for q in scored_questions:
        for flag in q.get("risk_flags", []):
            all_flags.append({
                "flag": flag,
                "domain": q.get("domain", "Unknown"),
                "question_id": q.get("question_id"),
                "score": q.get("score", 0),
            })

    # Sort by score ascending (lowest scored = highest risk)
    worst_questions = sorted(scored_questions, key=lambda x: x.get("score", 0))[:5]
    top_findings = [
        {
            "question_id": q.get("question_id"),
            "domain": q.get("domain"),
            "score": q.get("score"),
            "rationale": q.get("rationale", ""),
            "risk_flags": q.get("risk_flags", []),
        }
        for q in worst_questions
    ]

    return {
        "overall_score": overall_score,
        "risk_tier": risk_tier,
        "domain_scores": weighted_domain_scores,
        "top_findings": top_findings,
        "all_risk_flags": all_flags,
        "questions_scored": len(scored_questions),
    }
