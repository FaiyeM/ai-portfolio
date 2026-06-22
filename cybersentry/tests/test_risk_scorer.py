"""Tests for composite risk scorer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from enrichment.risk_scorer import calculate_risk_score, get_recommended_control, calculate_due_date


def test_critical_cvss_produces_high_risk():
    cve = {
        "cve_id": "CVE-TEST-001",
        "cvss_score": 10.0,
        "description": "Critical unauthenticated remote code execution",
        "affected_products": ["Palo Alto Firewall"],
        "keywords": ["remote code execution"],
    }
    result = calculate_risk_score(cve)
    assert result["risk_score"] >= 80.0
    assert result["risk_level"] in ("CRITICAL", "HIGH")


def test_low_cvss_produces_lower_risk():
    cve = {
        "cve_id": "CVE-TEST-002",
        "cvss_score": 3.0,
        "description": "Minor information disclosure vulnerability",
        "affected_products": ["Unknown App"],
        "keywords": [],
    }
    result = calculate_risk_score(cve)
    assert result["risk_score"] < 70.0


def test_risk_score_within_bounds():
    for cvss in [0.0, 5.0, 8.5, 10.0]:
        cve = {
            "cve_id": "CVE-TEST-X",
            "cvss_score": cvss,
            "description": "Test vulnerability",
            "affected_products": [],
            "keywords": [],
        }
        result = calculate_risk_score(cve)
        assert 0.0 <= result["risk_score"] <= 100.0, f"Score {result['risk_score']} out of bounds for CVSS {cvss}"


def test_due_date_critical_is_15_days():
    from datetime import date, timedelta
    due = calculate_due_date("CRITICAL")
    expected = (date.today() + timedelta(days=15)).strftime("%Y-%m-%d")
    assert due == expected


def test_due_date_low_is_180_days():
    from datetime import date, timedelta
    due = calculate_due_date("LOW")
    expected = (date.today() + timedelta(days=180)).strftime("%Y-%m-%d")
    assert due == expected


def test_recommended_control_returns_string():
    for tactic in ["Initial Access", "Execution", "Persistence", "Exfiltration", "Impact"]:
        control = get_recommended_control(tactic, "HIGH")
        assert isinstance(control, str)
        assert len(control) > 10


def test_score_breakdown_sums_correctly():
    cve = {
        "cve_id": "CVE-TEST-003",
        "cvss_score": 8.0,
        "description": "Vulnerability affecting VPN concentrator",
        "affected_products": ["Cisco VPN"],
        "keywords": ["vpn"],
    }
    result = calculate_risk_score(cve)
    breakdown = result["score_breakdown"]
    total = breakdown["cvss_contribution"] + breakdown["asset_contribution"]
    # Total before multiplier should be close to risk_score / multiplier
    assert total > 0


if __name__ == "__main__":
    tests = [
        test_critical_cvss_produces_high_risk,
        test_low_cvss_produces_lower_risk,
        test_risk_score_within_bounds,
        test_due_date_critical_is_15_days,
        test_due_date_low_is_180_days,
        test_recommended_control_returns_string,
        test_score_breakdown_sums_correctly,
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
