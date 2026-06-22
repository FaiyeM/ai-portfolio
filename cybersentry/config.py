"""Configuration loader for CyberSentry."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Anthropic
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# NVD
NVD_API_KEY: str = os.getenv("NVD_API_KEY", "")
NVD_BASE_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# ChromaDB
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# Output
OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./reports"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Sample data
SAMPLE_CVES_PATH: Path = Path(__file__).parent / "ingestion" / "sample_cves.json"
THREAT_DOCS_PATH: Path = Path(__file__).parent / "rag" / "threat_docs"

# Risk scoring weights
CVSS_WEIGHT: float = 0.6
ASSET_CRITICALITY_WEIGHT: float = 0.4

# MITRE ATT&CK tactics
MITRE_TACTICS = [
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Impact",
    "Command and Control",
]
