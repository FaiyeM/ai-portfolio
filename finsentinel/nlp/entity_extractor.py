"""spaCy NER — extract companies, currencies, and financial amounts from text.

Model: en_core_web_sm
Install: python -m spacy download en_core_web_sm
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def _get_nlp():
    """Load and cache spaCy model."""
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        nlp = spacy.load("en_core_web_sm")
    return nlp


def extract_entities(text: str) -> dict[str, list[str]]:
    """Extract named entities from financial news text.

    Returns:
        Dict with 'companies', 'currencies', 'amounts', 'locations', 'all_entities'
    """
    nlp = _get_nlp()
    doc = nlp(text[:1000])  # Limit for speed

    entities: dict[str, list[str]] = {
        "companies": [],
        "currencies": [],
        "amounts": [],
        "locations": [],
        "all_entities": [],
    }

    for ent in doc.ents:
        entities["all_entities"].append(f"{ent.text} ({ent.label_})")
        if ent.label_ in ("ORG", "PRODUCT"):
            entities["companies"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["amounts"].append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            entities["locations"].append(ent.text)
        elif ent.label_ == "PERCENT":
            entities["currencies"].append(ent.text)

    # Deduplicate
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))

    return entities
