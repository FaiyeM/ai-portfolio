"""Tests for MITRE ATT&CK mapper."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from enrichment.mitre_mapper import map_cve_to_mitre_demo


def test_maps_rce_to_initial_access():
    cve = {
        "cve_id": "CVE-TEST-001",
        "description": "A remote code execution vulnerability in an internet-facing application",
        "keywords": ["remote code execution"],
    }
    tactic, technique = map_cve_to_mitre_demo(cve)
    assert tactic == "Initial Access"
    assert "T1190" in technique


def test_maps_command_injection_to_execution():
    cve = {
        "cve_id": "CVE-TEST-002",
        "description": "Command injection allows attacker to execute arbitrary commands",
        "keywords": ["command injection"],
    }
    tactic, technique = map_cve_to_mitre_demo(cve)
    assert tactic == "Execution"
    assert "T1059" in technique


def test_maps_dos_to_impact():
    cve = {
        "cve_id": "CVE-TEST-003",
        "description": "A denial of service vulnerability causes service unavailability",
        "keywords": ["denial of service"],
    }
    tactic, technique = map_cve_to_mitre_demo(cve)
    assert tactic == "Impact"


def test_maps_credential_theft_to_credential_access():
    cve = {
        "cve_id": "CVE-TEST-004",
        "description": "Vulnerability exposes credential stores allowing credential theft",
        "keywords": ["credential access", "credentials"],
    }
    tactic, technique = map_cve_to_mitre_demo(cve)
    assert tactic == "Credential Access"


def test_returns_string_tuple():
    cve = {
        "cve_id": "CVE-TEST-005",
        "description": "A generic vulnerability with no specific keywords",
        "keywords": [],
    }
    result = map_cve_to_mitre_demo(cve)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)


if __name__ == "__main__":
    tests = [
        test_maps_rce_to_initial_access,
        test_maps_command_injection_to_execution,
        test_maps_dos_to_impact,
        test_maps_credential_theft_to_credential_access,
        test_returns_string_tuple,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
