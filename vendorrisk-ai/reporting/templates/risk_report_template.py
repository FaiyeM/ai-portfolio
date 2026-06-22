"""ReportLab style constants and reusable layout components for VendorRisk AI reports.

This module provides shared styles, colour palette, and helper builders
used by reporting/pdf_generator.py. Import here keeps the generator clean.
"""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Brand colour palette ──────────────────────────────────────────────────
BRAND_DARK = colors.HexColor("#1A2B4A")      # Deep navy — headers
BRAND_ACCENT = colors.HexColor("#2E6DA4")    # Corporate blue — accents
BRAND_LIGHT = colors.HexColor("#E8F0F7")     # Light blue — table alternates
BRAND_SUCCESS = colors.HexColor("#27AE60")   # Green — LOW risk
BRAND_WARNING = colors.HexColor("#F39C12")   # Amber — MEDIUM risk
BRAND_DANGER = colors.HexColor("#E74C3C")    # Red — HIGH / CRITICAL risk
BRAND_NEUTRAL = colors.HexColor("#7F8C8D")   # Grey — neutral text

# ── Risk tier colours ─────────────────────────────────────────────────────
RISK_TIER_COLOURS = {
    "LOW": BRAND_SUCCESS,
    "MEDIUM": BRAND_WARNING,
    "HIGH": BRAND_DANGER,
    "CRITICAL": colors.HexColor("#8E44AD"),
}

# ── Page margins (mm) ─────────────────────────────────────────────────────
PAGE_MARGIN_LEFT = 20 * mm
PAGE_MARGIN_RIGHT = 20 * mm
PAGE_MARGIN_TOP = 25 * mm
PAGE_MARGIN_BOTTOM = 20 * mm


def build_styles() -> dict:
    """Return a dict of named ParagraphStyles for report sections."""
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=24,
            textColor=BRAND_DARK,
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontSize=13,
            textColor=BRAND_ACCENT,
            spaceAfter=12,
            alignment=TA_LEFT,
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            parent=base["Heading2"],
            fontSize=13,
            textColor=BRAND_DARK,
            spaceBefore=14,
            spaceAfter=6,
            borderPad=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            leading=15,
            textColor=colors.black,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontSize=8,
            textColor=BRAND_NEUTRAL,
            alignment=TA_CENTER,
        ),
        "finding_high": ParagraphStyle(
            "FindingHigh",
            parent=base["Normal"],
            fontSize=10,
            textColor=BRAND_DANGER,
            leftIndent=8,
        ),
        "finding_medium": ParagraphStyle(
            "FindingMedium",
            parent=base["Normal"],
            fontSize=10,
            textColor=BRAND_WARNING,
            leftIndent=8,
        ),
        "finding_low": ParagraphStyle(
            "FindingLow",
            parent=base["Normal"],
            fontSize=10,
            textColor=BRAND_SUCCESS,
            leftIndent=8,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.black,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontSize=8,
            textColor=BRAND_NEUTRAL,
            alignment=TA_CENTER,
        ),
    }
    return styles


def risk_tier_badge_colour(risk_tier: str) -> colors.Color:
    """Return the ReportLab colour for a given risk tier string."""
    return RISK_TIER_COLOURS.get(risk_tier.upper(), BRAND_NEUTRAL)


def domain_score_colour(score: float) -> colors.Color:
    """Return a colour based on a 0-100 domain score."""
    if score >= 80:
        return BRAND_SUCCESS
    elif score >= 60:
        return BRAND_WARNING
    else:
        return BRAND_DANGER


# ── Standard table styles ─────────────────────────────────────────────────
def base_table_style() -> list:
    """Return a TableStyle list for standard report tables."""
    return [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
