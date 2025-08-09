# Auto-install nltk if missing
try:
    import nltk
except ModuleNotFoundError:
    import os
    os.system("pip install nltk")
    import nltk

# src/builder.py

import re
import nltk

# Download NLTK resources once (safe to leave in here)
#try:
    #nltk.data.find('tokenizers/punkt')
#except LookupError:
    #nltk.download('punkt')

#try:
    #nltk.data.find('taggers/averaged_perceptron_tagger')
#except LookupError:
    #nltk.download('averaged_perceptron_tagger')
    

# Auto-download required NLTK resources if missing (first run only)
def _ensure_nltk_data():
    required = {
        "tokenizers": ["punkt", "punkt_tab"],
        "taggers": ["averaged_perceptron_tagger"],
    }
    for subdir, packages in required.items():
        for pkg in packages:
            try:
                nltk.data.find(f"{subdir}/{pkg}")
            except LookupError:
                nltk.download(pkg)

_ensure_nltk_data()



# =========================
# STAR Algorithm
# =========================
SITUATION_KWS = {"faced", "during", "as part of", "legacy", "outdated", "bottleneck", "issue", "problem", "pain point", "context", "assigned"}
TASK_KWS      = {"responsible", "tasked", "goal", "target", "deadline", "in charge", "ownership", "scope"}
ACTION_KWS    = {"led", "built", "created", "developed", "implemented", "refactored", "designed", "tested", "automated",
                 "integrated", "migrated", "optimized", "configured", "fixed", "collaborated", "coordinated", "deployed"}
RESULT_KWS    = {"improved", "increased", "reduced", "decreased", "saved", "cut", "boosted", "achieved", "resulted",
                 "grew", "accelerated", "faster", "lower", "%", "x", "kpi", "sla", "uptime"}

def _classify_sentence(sent: str) -> str:
    s = sent.strip().lower()
    if any(kw in s for kw in RESULT_KWS):    return "R"
    if any(kw in s for kw in ACTION_KWS):    return "A"
    if any(kw in s for kw in TASK_KWS):      return "T"
    if any(kw in s for kw in SITUATION_KWS): return "S"

    # POS fallback
    tokens = nltk.word_tokenize(sent)
    if not tokens:
        return "U"
    pos = nltk.pos_tag(tokens)
    if any(t.startswith("VB") for _, t in pos):  # verb
        return "A"
    if any(t.startswith("NN") for _, t in pos):  # noun
        return "S"
    return "U"

def _clean_clause(s: str) -> str:
    s = s.strip().rstrip(".")
    if not s:
        return s
    return s[0].upper() + s[1:]

def star_bullets_from_summary(summary: str, max_bullets: int = 4):
    """Convert raw summary text into STAR-style bullet points."""
    sentences = [x.strip() for x in re.split(r'(?<=[.!?])\s+|\n+', summary) if x.strip()]
    if not sentences:
        return []

    # Classify sentences
    buckets = {"S": [], "T": [], "A": [], "R": [], "U": []}
    for sent in sentences:
        tag = _classify_sentence(sent)
        buckets[tag].append(sent)

    bullets = []
    used = set()

    def take(bucket_key):
        while buckets[bucket_key]:
            cand = buckets[bucket_key].pop(0)
            if cand not in used:
                used.add(cand)
                return cand
        return None

    for _ in range(max_bullets):
        s_or_t = take("S") or take("T")
        a1 = take("A")
        r  = take("R")
        a2 = take("A") if a1 and len(bullets) % 2 == 0 else None

        if not (s_or_t or a1 or r):
            break

        parts = []
        if s_or_t:
            parts.append(_clean_clause(s_or_t))
        if a1:
            a_text = _clean_clause(a1) if not s_or_t else a1.strip().rstrip(".")
            parts.append(("," if s_or_t else "") + f" {a_text}")
        if a2:
            parts.append(f" and {a2.strip().rstrip('.')}")
        if r:
            connector = " resulting in " if (s_or_t or a1 or a2) else ""
            parts.append(connector + r.strip().rstrip("."))

        line = "".join(parts).strip()
        if not line.endswith("."):
            line += "."
        bullets.append(f"• {line}")

    return bullets


# =========================
# XYZ Algorithm (Projects & Extracurriculars)
# =========================
def xyz_bullets_from_summary(summary: str, max_bullets: int = 3):
    """
    Convert raw summary into XYZ bullets:
    - X = What you did
    - Y = Measurable outcome
    - Z = Context/tools
    """
    sents = [s.strip().rstrip(".") for s in re.split(r'(?<=[.!?])\s+|\n+', summary) if s.strip()]
    bullets = []
    for s in sents:
        has_metric = any(tok in s.lower() for tok in ["%", "x", "increased", "reduced", "improved", "decreased", "saved"])
        text = s[0].upper() + s[1:]
        if has_metric:
            bullets.append(f"• {text}.")
        else:
            bullets.append(f"• {text} (quantified where possible).")
        if len(bullets) >= max_bullets:
            break
    return bullets or ["• Completed project work; quantified impact where possible."]


# =========================
# Main builder function
# =========================
def build_resume(raw: dict) -> dict:
    """
    Turn raw input from questions.py into structured, bullet-ready data for the PDF.
    """
    print("running build_resume")
    structured = {
        "contact": raw.get("contact", {}),
        "education": raw.get("education", []),
        "skills": raw.get("skills", {}),
        "experience": [],
        "projects": [],
        "extracurriculars": []
    }

    # Experiences → STAR bullets
    for exp in raw.get("experience", []):
        summary = exp.get("summary", "")
        bullets = star_bullets_from_summary(summary, max_bullets=4)
        structured["experience"].append({
            "title": exp.get("title", ""),
            "company": exp.get("company", ""),
            "location": exp.get("location", ""),
            "dates": exp.get("dates", ""),
            "bullets": bullets
        })

    # Projects → XYZ bullets
    for proj in raw.get("projects", []):
        summary = proj.get("summary", "")
        bullets = xyz_bullets_from_summary(summary, max_bullets=3)
        structured["projects"].append({
            "title": proj.get("title", ""),
            "tools": proj.get("tools", ""),
            "dates": proj.get("dates", ""),
            "bullets": bullets
        })

    # Extracurriculars → XYZ bullets
    for ex in raw.get("extracurriculars", []):
        summary = ex.get("summary", "")
        bullets = xyz_bullets_from_summary(summary, max_bullets=2)
        structured["extracurriculars"].append({
            "title": ex.get("title", ""),
            "dates": ex.get("dates", ""),
            "bullets": bullets
        })

    return structured
if __name__ == "__main__":
    test_text = "I led a team of 5 engineers to build a secure login system in Python using Flask and JWT tokens."
    print("Original Summary:\n", test_text)
    bullet_points = build_resume(test_text)
    print("\nGenerated Bullet Points:")
    for point in bullet_points:
        print("- " + point)

