"""Score all questions in a vendor questionnaire response."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_questionnaire(questionnaire_name: str) -> dict[str, Any]:
    """Load questionnaire JSON from the questionnaires/ folder."""
    q_dir = Path(__file__).parent.parent / "questionnaires"
    name_map = {
        "default": "default_questionnaire.json",
        "financial_sector": "financial_sector.json",
    }
    filename = name_map.get(questionnaire_name, "default_questionnaire.json")
    path = q_dir / filename
    if not path.exists():
        path = q_dir / "default_questionnaire.json"
    with open(path) as f:
        return json.load(f)


def load_vendor_responses(vendor_name: str, questionnaire: str = "default") -> dict[str, Any]:
    """Load vendor responses from sample_data or accept a dict directly."""
    sample_dir = Path(__file__).parent.parent / "sample_data"

    # Try to find a matching sample file
    for f in sample_dir.glob("*.json"):
        data = json.loads(f.read_text())
        if vendor_name.lower().replace(" ", "") in data.get("vendor_name", "").lower().replace(" ", ""):
            return data

    raise FileNotFoundError(
        f"No sample data found for vendor '{vendor_name}'. "
        f"Available: {[f.stem for f in sample_dir.glob('*.json')]}"
    )


def score_all_questions(
    questionnaire: dict[str, Any],
    vendor_responses: dict[str, Any],
    analyst,
) -> list[dict[str, Any]]:
    """Score all questions in the questionnaire against vendor responses.

    Args:
        questionnaire: Loaded questionnaire dict
        vendor_responses: Loaded vendor response dict
        analyst: VendorRiskAnalyst instance

    Returns:
        List of scored question dicts
    """
    responses = vendor_responses.get("responses", {})
    vendor_name = vendor_responses.get("vendor_name", "Unknown")
    scored = []

    for domain_obj in questionnaire.get("domains", []):
        domain = domain_obj["domain"]
        for q in domain_obj.get("questions", []):
            q_id = q["id"]
            response = responses.get(str(q_id), "No response provided.")
            score_result = analyst.score_response(
                domain=domain,
                question_id=q_id,
                question=q["question"],
                response=response,
                vendor_name=vendor_name,
            )
            scored.append(score_result)

    return scored
