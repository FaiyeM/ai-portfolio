"""Configurable domain weights for vendor risk scoring."""

DEFAULT_DOMAIN_WEIGHTS = {
    "Data Security & Privacy": 0.30,
    "Business Continuity & DR": 0.25,
    "Third-Party Sub-processors": 0.15,
    "Regulatory Compliance": 0.15,
    "Incident Response": 0.15,
}

FINANCIAL_SECTOR_WEIGHTS = {
    "Data Security & Privacy": 0.25,
    "Business Continuity & DR": 0.30,
    "Third-Party Sub-processors": 0.15,
    "Regulatory Compliance": 0.20,
    "Incident Response": 0.10,
}


def get_weights(questionnaire_name: str) -> dict[str, float]:
    if "financial" in questionnaire_name.lower():
        return FINANCIAL_SECTOR_WEIGHTS
    return DEFAULT_DOMAIN_WEIGHTS
