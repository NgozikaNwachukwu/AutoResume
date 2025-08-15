# src/pdf_generator.py

from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch


# ---- Styles (monochrome, Helvetica) ----
def _styles():
    base = getSampleStyleSheet()
    black = colors.black
    return {
        "name": ParagraphStyle(
            "name",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            alignment=TA_CENTER,
            textColor=black,
            spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "contact",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            alignment=TA_CENTER,
            textColor=black,
            spaceAfter=10,
        ),
        "section": ParagraphStyle(
            "section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14,
            alignment=TA_LEFT,
            textColor=black,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "subhead_bold": ParagraphStyle(
            "subhead_bold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            alignment=TA_LEFT,
            textColor=black,
            spaceAfter=0,
        ),
        "subhead_ital": ParagraphStyle(
            "subhead_ital",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=12,
            alignment=TA_LEFT,
            textColor=black,
            spaceAfter=0,
        ),
        "right_small": ParagraphStyle(
            "right_small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            alignment=TA_RIGHT,
            textColor=black,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            alignment=TA_LEFT,
            textColor=black,
            spaceAfter=0,
        ),
        "skill": ParagraphStyle(
            "skill",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            alignment=TA_LEFT,
            textColor=black,
            spaceAfter=1,
        ),
    }


# ---- Utilities ----
def _hr():
    return HRFlowable(
        width="100%",
        thickness=1,
        color=colors.black,
        spaceBefore=2,
        spaceAfter=4,
    )


def _caps(s: str) -> str:
    return (s or "").upper()


def _contact_line(c: dict) -> str:
    bits = []
    loc = c.get("location") or c.get("Location")
    if c.get("email"):
        bits.append(c["email"])
    if c.get("phone"):
        bits.append(c["phone"])
    if c.get("linkedin"):
        bits.append(c["linkedin"])
    if c.get("github"):
        bits.append(c["github"])
    if c.get("portfolio"):
        bits.append(c["portfolio"])
    if loc:
        bits.insert(0, loc)
    return " • ".join(bits)


def _two_col_row(
    left_para, right_para, styles, col_ratio=(0.72, 0.28), pad=(0, 0, 0, 0)
):
    t = Table(
        [
            [
                Paragraph(left_para, styles["subhead_bold"]),
                Paragraph(right_para, styles["right_small"]),
            ]
        ],
        colWidths=[col_ratio[0] * 6.5 * inch, col_ratio[1] * 6.5 * inch],
        hAlign="LEFT",
    )
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), pad[0]),
                ("TOPPADDING", (0, 0), (-1, -1), pad[1]),
                ("RIGHTPADDING", (0, 0), (-1, -1), pad[2]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad[3]),
            ]
        )
    )
    return t


def _subrow(left_text, right_text, styles):
    t = Table(
        [
            [
                Paragraph(left_text, styles["subhead_ital"]),
                Paragraph(right_text, styles["right_small"]),
            ]
        ],
        colWidths=[0.72 * 6.5 * inch, 0.28 * 6.5 * inch],
        hAlign="LEFT",
    )
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return t


def _bullets(styles, items):
    pars = []
    for raw in items or []:
        t = str(raw).lstrip("• ").rstrip(".")
        pars.append(ListItem(Paragraph(t + ".", styles["body"]), leftIndent=6))
    return ListFlowable(pars, bulletType="bullet", leftIndent=14)


# ---- Public API ----
def build_pdf(structured: dict, filename: str = "AutoResume.pdf"):
    S = _styles()

    doc = SimpleDocTemplate(
        filename,
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="AutoResume",
        author=(structured.get("contact", {}) or {}).get("full_name", ""),
    )
    story = []

    # NAME + CONTACT
    contact = structured.get("contact", {})
    name = contact.get("full_name") or contact.get("Full name") or ""
    if name:
        story.append(Paragraph(name, S["name"]))
    contact_line = _contact_line(contact)
    if contact_line:
        story.append(Paragraph(contact_line, S["contact"]))
    story.append(Spacer(1, 6))

    # EDUCATION
    edu = structured.get("education", [])
    if edu:
        story.append(Paragraph(_caps("Education"), S["section"]))
        story.append(_hr())
        for ed in edu:
            school = (ed.get("school") or "").strip()
            degree = (ed.get("degree") or "").strip()
            loc = (ed.get("location") or "").strip()
            dates = (ed.get("date") or ed.get("dates") or "").strip()

            gpa = ed.get("GPA") or ed.get("gpa")
            if gpa:
                degree = f"{degree} — GPA: {gpa}"

            story.append(_two_col_row(school, loc, S))
            story.append(_subrow(degree, dates, S))
            story.append(Spacer(1, 6))

    # EXPERIENCE
    exp = structured.get("experience", [])
    if exp:
        story.append(Paragraph(_caps("Experience"), S["section"]))
        story.append(_hr())
        for e in exp:
            title = (e.get("title") or "").strip()
            company = (e.get("company") or "").strip()
            loc = (e.get("location") or "").strip()
            dates = (e.get("dates") or e.get("date") or "").strip()

            story.append(_two_col_row(title, dates, S))
            story.append(_subrow(company, loc, S))

            bullets = e.get("bullets", [])
            if bullets:
                story.append(_bullets(S, bullets))
                story.append(Spacer(1, 6))

    # PROJECTS
    projects = structured.get("projects", [])
    if projects:
        story.append(Paragraph(_caps("Projects"), S["section"]))
        story.append(_hr())
        for p in projects:
            title = (p.get("title") or "").strip()

            # Handle tools as string OR list
            val = p.get("tools")
            if isinstance(val, list):
                tools = ", ".join(map(str, val))
            else:
                tools = (val or "").strip()

            dates = (p.get("dates") or p.get("date") or "").strip()

            left = f"{title}" + (f" | {tools}" if tools else "")
            story.append(_two_col_row(left, dates, S))
            bullets = p.get("bullets", [])
            if bullets:
                story.append(_bullets(S, bullets))
            story.append(Spacer(1, 6))

    # TECHNICAL SKILLS
    skills = structured.get("skills", {})
    if skills:
        story.append(Paragraph(_caps("Technical Skills"), S["section"]))
        story.append(_hr())
        for category, items in skills.items():
            if isinstance(items, (list, tuple)):
                txt = ", ".join([str(x).strip() for x in items if str(x).strip()])
            else:
                txt = str(items)
            story.append(Paragraph(f"<b>{category}:</b> {txt}", S["skill"]))
        story.append(Spacer(1, 6))

    # EXTRACURRICULARS
    extras = structured.get("extracurriculars", [])
    if extras:
        story.append(Paragraph(_caps("Extracurriculars"), S["section"]))
        story.append(_hr())
        for ex in extras:
            title = (ex.get("title") or "").strip()
            dates = (ex.get("dates") or ex.get("date") or "").strip()
            story.append(_two_col_row(title, dates, S))
            bullets = ex.get("bullets", [])
            if bullets:
                story.append(_bullets(S, bullets))
            story.append(Spacer(1, 6))

    doc.build(story)
    return filename
