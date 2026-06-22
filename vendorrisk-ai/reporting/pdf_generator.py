"""PDF risk report generator using ReportLab."""
from __future__ import annotations

import io
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

RISK_COLORS = {
    "LOW": colors.HexColor("#27ae60"),
    "MEDIUM": colors.HexColor("#f39c12"),
    "HIGH": colors.HexColor("#e67e22"),
    "CRITICAL": colors.HexColor("#e74c3c"),
}


def _make_radar_chart(domain_scores: dict[str, Any]) -> io.BytesIO:
    """Generate a radar/spider chart of domain scores."""
    domains = list(domain_scores.keys())
    scores = [v["score_out_of_100"] for v in domain_scores.values()]
    n = len(domains)

    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    scores_plot = scores + [scores[0]]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, scores_plot, "o-", linewidth=2, color="#2980b9")
    ax.fill(angles, scores_plot, alpha=0.25, color="#2980b9")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([d.replace(" & ", "\n& ") for d in domains], size=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], size=7)
    ax.set_title("Domain Score Radar", pad=20, fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_report(
    vendor_name: str,
    assessment_date: str,
    aggregation: dict[str, Any],
    scored_questions: list[dict[str, Any]],
    remediation: dict[str, Any],
    output_filename: str | None = None,
) -> Path:
    """Generate a PDF risk report for a vendor assessment."""
    if output_filename is None:
        safe_name = vendor_name.replace(" ", "_").lower()
        output_filename = f"{safe_name}_risk_report.pdf"

    output_path = OUTPUT_DIR / output_filename
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── COVER PAGE ───────────────────────────────────────────────── #
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#1a252f"), spaceAfter=0.4 * cm)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12, textColor=colors.grey)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#2c3e50"), spaceBefore=0.5 * cm)
    h3_style = ParagraphStyle("H3", parent=styles["Heading3"], textColor=colors.HexColor("#34495e"))

    story += [
        Spacer(1, 1 * cm),
        Paragraph("Vendor Risk Assessment Report", title_style),
        Paragraph(f"Vendor: <b>{vendor_name}</b>", sub_style),
        Paragraph(f"Assessment Date: {assessment_date}", sub_style),
        Paragraph(f"Prepared by: VendorRisk AI (Anthropic Claude)", sub_style),
        Spacer(1, 0.5 * cm),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2c3e50")),
        Spacer(1, 0.5 * cm),
    ]

    # ── EXECUTIVE SUMMARY ────────────────────────────────────────── #
    risk_tier = aggregation["risk_tier"]
    overall_score = aggregation["overall_score"]
    risk_color = RISK_COLORS.get(risk_tier, colors.grey)

    story += [
        Paragraph("Executive Summary", h2_style),
        Paragraph(remediation.get("executive_summary", ""), body_style),
        Spacer(1, 0.4 * cm),
    ]

    # Score summary table
    exec_table_data = [
        ["Metric", "Value"],
        ["Overall Risk Score", f"{overall_score}/100"],
        ["Risk Tier", risk_tier],
        ["Questions Scored", str(aggregation["questions_scored"])],
        ["Risk Flags Identified", str(len(aggregation.get("all_risk_flags", [])))],
    ]
    exec_table = Table(exec_table_data, colWidths=[8 * cm, 8 * cm])
    exec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (1, 2), (1, 2), risk_color),
        ("TEXTCOLOR", (1, 2), (1, 2), colors.white),
        ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [exec_table, Spacer(1, 0.5 * cm)]

    # ── DOMAIN SCORES ────────────────────────────────────────────── #
    story.append(Paragraph("Domain Score Summary", h2_style))

    domain_table_data = [["Domain", "Score/100", "Weight", "Contribution"]]
    for domain, data in aggregation["domain_scores"].items():
        domain_table_data.append([
            domain,
            f"{data['score_out_of_100']:.0f}",
            f"{data['weight']:.0%}",
            f"{data['weighted_contribution']:.1f}",
        ])
    domain_table_data.append(["OVERALL", f"{overall_score}", "", ""])

    domain_table = Table(domain_table_data, colWidths=[8 * cm, 3 * cm, 2.5 * cm, 3 * cm])
    domain_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecf0f1")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f9f9f9")]),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [domain_table, Spacer(1, 0.5 * cm)]

    # Radar chart
    try:
        radar_buf = _make_radar_chart(aggregation["domain_scores"])
        story += [Image(radar_buf, width=10 * cm, height=10 * cm), Spacer(1, 0.5 * cm)]
    except Exception:
        pass

    # ── TOP 5 RISK FINDINGS ──────────────────────────────────────── #
    story += [PageBreak(), Paragraph("Top 5 Risk Findings", h2_style)]

    for i, finding in enumerate(aggregation.get("top_findings", []), 1):
        score = finding.get("score", 0)
        severity = "CRITICAL" if score <= 2 else "HIGH" if score <= 4 else "MEDIUM" if score <= 6 else "LOW"
        sev_color = RISK_COLORS.get(severity, colors.grey)

        finding_data = [
            [f"Finding {i}: Q{finding.get('question_id')} — {finding.get('domain', 'Unknown')}",
             f"Score: {score}/10 [{severity}]"],
            [finding.get("rationale", ""), ""],
        ]
        ft = Table(finding_data, colWidths=[12 * cm, 4.5 * cm])
        ft.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ecf0f1")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (1, 0), (1, 0), sev_color),
            ("TEXTCOLOR", (1, 0), (1, 0), colors.white),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
            ("SPAN", (0, 1), (-1, 1)),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story += [ft, Spacer(1, 0.3 * cm)]

    # ── REMEDIATION ACTIONS ──────────────────────────────────────── #
    story += [Spacer(1, 0.5 * cm), Paragraph("Recommended Remediation Actions", h2_style)]

    remediation_actions = remediation.get("remediation_actions", [])
    rem_data = [["Priority", "Action", "Timeline"]]
    for action in remediation_actions:
        rem_data.append([
            action.get("priority", ""),
            action.get("action", ""),
            action.get("timeline", ""),
        ])

    rem_table = Table(rem_data, colWidths=[3 * cm, 11 * cm, 2.5 * cm])
    rem_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("WORDWRAP", (1, 0), (1, -1), True),
    ]))
    story += [rem_table, Spacer(1, 1 * cm)]

    story += [
        Paragraph(
            f"<i>Report generated by VendorRisk AI on {date.today()}. Powered by Anthropic Claude.</i>",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
        )
    ]

    doc.build(story)
    return output_path
