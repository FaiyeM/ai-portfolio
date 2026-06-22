"""Configuration for ComplianceRAG."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K: int = int(os.getenv("TOP_K", "5"))

REGULATORY_DOCS_PATH: Path = Path(__file__).parent / "ingestion" / "regulatory_docs"

FRAMEWORKS = {
    "APRA CPS 234": "apra_cps234_summary.md",
    "ISO 27001": "iso27001_controls.md",
    "SOC 2": "soc2_trust_criteria.md",
    "All": None,
}
