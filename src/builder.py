# ======================
# src/builder.py
# ======================

# --- deps: auto-install + data check ---
# Auto-install nltk if missing (safer subprocess form)
try:
    import nltk
except ModuleNotFoundError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    import nltk

import re
import copy

# Auto-download required NLTK resources if missing (first run only)
def _ensure_nltk_data():
    required = {
        "tokenizers": ["punkt", "punkt_tab"],  # include punkt_tab for newer NLTK
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
# Rewrite helpers
# =========================

# Strong verbs to anchor bullet openings/promotions
ACTION_VERBS = {
    "built","created","developed","implemented","designed","automated","tested",
    "led","migrated","optimized","configured","fixed","integrated","deployed",
    "refactored","improved","reduced","increased","coordinated","collaborated",
    "managed","launched","delivered","orchestrated","owned","enhanced",
    # NEW (so we don't drop good openings like "Collected ...")
    "collected","analyzed","maintained","monitored","supported","documented","validated"
}

# Weak intros to strip
WEAK_PREFIXES = [
    r"i\s+(was\s+)?(responsible\s+for|tasked\s+with|tasked\s+to)\s+",
    r"i\s+(helped|assisted)\s+to\s+",
    r"i\s+(helped|assisted)\s+",
    r"\bwe\s+",
    r"my role (was|included)\s+",
    r"\bi\s+was\s+in\s+charge\s+of\s+",
    # NEW: handle "Was responsible for ..." with no pronoun
    r"^(was|were)\s+responsible\s+for\s+",
]

# Passive → active light normalizations
PASSIVE_TO_ACTIVE = [
    (r"\bwas\b\s+(tested|built|created|developed|implemented|designed|managed)\b", r"\1"),
    (r"\bwere\b\s+(tested|built|created|developed|implemented|designed|managed)\b", r"\1"),
]

# Detect trailing tech/tools clause (“using/with/in/via/through …”)
TECH_SPLIT = r"(?:using|with|in|via|through)\s+(.+)$"

def _clean_sentence(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".")
    return s

def _capitalize_tech(s: str) -> str:
    # light normalization for common tech names
    tech = []
    for t in re.split(r"\s*,\s*|\s+and\s+", s):
        t = t.strip()
        if not t:
            continue
        tl = t.lower()
        if tl in {
            "python","java","javascript","typescript","docker","kubernetes","git",
            "github","flask","django","react","azure","aws","gcp","sql","jenkins",
            "github actions","command line","cli","pandas","numpy","pytest","selenium"
        }:
            # special-casing a few multi-word tech labels
            if tl == "github actions":
                tech.append("GitHub Actions")
            elif tl in {"command line","cli"}:
                tech.append("command line")
            else:
                tech.append(t.capitalize())
        else:
            tech.append(t)
    return ", ".join([x for x in tech if x])

def _has_number(s: str) -> bool:
    return bool(re.search(r"\b\d+%?|\b\d+\b", s))

# gerund→past (creating→created)
def _gerund_to_past(word: str) -> str:
    base = re.sub(r"ing$", "", word)
    if not base:
        return word
    if base.endswith("y"):
        return base[:-1] + "ied"
    if base.endswith("e"):
        return base + "d"
    return base + "ed"

# promote “(I/We) was/were tasked with|to <gerund> …” → “<Verb-ed> …”
def _promote_tasked_phrases(s: str) -> str:
    s = re.sub(r"^(i|we)\s+(was|were)\s+tasked\s+(with|to)\s+", "", s, flags=re.I)
    s = re.sub(r"^was\s+tasked\s+(with|to)\s+", "", s, flags=re.I)
    m = re.match(r"^([a-z]+)ing\b(.*)$", s, flags=re.I)
    if m:
        first = _gerund_to_past(m.group(1)).capitalize()
        rest = m.group(2)
        s = f"{first}{rest}"
    return s

# collapse repeated gerunds (“…, managing …, managing …” → “…, managing … and …”)
def _dedupe_repeated_gerunds(s: str) -> str:
    s = re.sub(r"\b,\s*managing\b\s+", " and ", s, flags=re.I)
    s = re.sub(r"\b,\s*creating\b\s+", " and ", s, flags=re.I)
    return s

def _strong_opening(s: str) -> str:
    s = s.strip()
    s = _promote_tasked_phrases(s)

    # NEW: drop naked auxiliaries at start (e.g., “Was creating …” → “creating …”)
    s = re.sub(r"^(was|were)\s+", "", s, flags=re.I)

    # strip pronouns
    s = re.sub(r"^(i|we)\s+", "", s, flags=re.I)

    # strip weak prefixes
    for pat in WEAK_PREFIXES:
        s = re.sub(pat, "", s, flags=re.I)

    # passive → active
    for pat, rep in PASSIVE_TO_ACTIVE:
        s = re.sub(pat, rep, s, flags=re.I)

    s = _dedupe_repeated_gerunds(s)

    # If we now start with a gerund, convert to past (“creating”→“Created”)
    m = re.match(r"^([A-Za-z]+)ing\b(.*)$", s)
    if m:
        s = _gerund_to_past(m.group(1)).capitalize() + m.group(2)

    # Promote the FIRST action verb that appears in the sentence
    words = s.split()
    if words:
        first = words[0].lower()
        if first not in ACTION_VERBS:
            m = re.search(r"\b(" + "|".join(ACTION_VERBS) + r")\b", s, flags=re.I)
            if m:
                verb = m.group(1)
                # move earliest action verb to the front, keep the rest
                s = verb.capitalize() + " " + re.sub(
                    r".*?\b" + re.escape(verb) + r"\b", "", s, count=1, flags=re.I
                ).strip()

    # NEW: fallback — force verb-led bullet if nothing matched
    if not re.match(r"^(" + "|".join(ACTION_VERBS) + r")\b", s, flags=re.I):
        s = "Delivered " + s

    # Final: ensure initial capital
    return s[0:1].upper() + s[1:] if s else s

# generic fallback (kept for dev/testing)
def rewrite_to_resume_bullets(summary: str) -> list[str]:
    from nltk.tokenize import sent_tokenize
    bullets = []
    for sent in sent_tokenize(summary or ""):
        sent = _clean_sentence(sent)
        if not sent:
            continue
        tech = None
        m = re.search(TECH_SPLIT, sent, flags=re.I)
        if m:
            tech = _capitalize_tech(m.group(1))
            sent = sent[:m.start()].strip()
        sent = _strong_opening(sent)
        core = sent + (f" using {tech}" if tech else "")
        bullets.append("• " + core.rstrip(".") + ".")
    # dedupe and cap at 4
    seen, final = set(), []
    for b in bullets:
        k = b.lower()
        if k not in seen:
            seen.add(k)
            final.append(b)
        if len(final) == 4:
            break
    return final

# =========================
# STAR + XYZ converters
# =========================

_RESULT_PHRASES = [
    "improving reliability",
    "reducing manual effort",
    "speeding up feedback cycles",
    "enhancing usability",
    "increasing test coverage",
    "supporting on-time delivery",
]

def _tools_phrase_for(val):
    # expects str or list; returns ' using X, Y' or ''
    if not val:
        return ""
    if isinstance(val, str):
        cleaned = _capitalize_tech(val)
    else:
        cleaned = _capitalize_tech(", ".join([str(x) for x in val if x]))
    return f" using {cleaned}" if cleaned else ""

def make_star_bullets(summary: str, role: str = "", org: str = "", tools=None) -> list[str]:
    """
    STAR-ish (3 bullets): Situation/Task, Action, Result.
    Rule-based, never fabricates numbers.
    """
    from nltk.tokenize import sent_tokenize
    sents = [_clean_sentence(s) for s in sent_tokenize(summary or "") if _clean_sentence(s)]
    joined = " ".join(sents)

    # Bullet 1 — Situation/Task
    task = sents[0] if sents else (role or "key responsibilities")
    b1 = _strong_opening(task)
    b1 = "• " + b1.rstrip(".") + "."

    # Bullet 2 — Action (with tools)
    action = sents[1] if len(sents) > 1 else "Implemented improvements"
    b2 = _strong_opening(action) + _tools_phrase_for(tools)
    b2 = "• " + b2.rstrip(".") + "."

    # Bullet 3 — Result (generic but honest)
    res = _RESULT_PHRASES[len(joined) % len(_RESULT_PHRASES)]
    b3 = "• " + ("Delivered measurable outcomes by " + res).rstrip(".") + "."

    return [b1, b2, b3]

def make_xyz_bullets(summary: str, tools=None, max_bullets: int = 2) -> list[str]:
    """
    XYZ: Delivered X (what) by doing Z (how){ using tools}, improving Y (impact).
    1–2 concise bullets.
    """
    from nltk.tokenize import sent_tokenize
    sents = [_clean_sentence(s) for s in sent_tokenize(summary or "") if _clean_sentence(s)]
    if not sents:
        return []

    what = sents[0]
    how  = sents[1] if len(sents) > 1 else "implementing core features and tests"
    impact = _RESULT_PHRASES[len(what) % len(_RESULT_PHRASES)]

    b1 = f"• Delivered {what} by {how}{_tools_phrase_for(tools)}, {impact}."
    bullets = [b1]

    # Optional detail bullet from remaining sentences
    for d in sents[2:][:max(0, max_bullets - 1)]:
        bullets.append("• Documented and validated " + _strong_opening(d).rstrip(".") + ".")

    return bullets[:max_bullets]

# =========================
# Main builder function
# =========================
def build_resume(raw: dict) -> dict:
    """
    Turn raw input from questions.py into structured, bullet-ready data for the PDF.
      - Experience   → STAR (3 bullets)
      - Projects     → XYZ  (≤2 bullets)
      - Extracurrics → XYZ  (≤2 bullets)
    """
    structured = {
        "contact": raw.get("contact", {}),
        "education": raw.get("education", []),
        "skills": raw.get("skills", {}),
        "experience": [],
        "projects": [],
        "extracurriculars": []
    }

    # --- Experiences → STAR ---
    for exp in raw.get("experience", []):
        # Accept either 'summary' or a list of 'bullets' typed by the user
        source_text = " ".join(exp.get("bullets", [])) or exp.get("summary", "") or ""
        bullets = make_star_bullets(
            source_text,
            role=exp.get("title", ""),
            org=exp.get("company", ""),
            tools=exp.get("tools") or exp.get("stack") or exp.get("tech")
        ) if source_text else []

        structured["experience"].append({
            "title": exp.get("title", ""),
            "company": exp.get("company", ""),
            "location": exp.get("location", ""),
            "dates": exp.get("dates", exp.get("date", "")),
            "bullets": bullets[:3]   # cap at 3
        })

    # --- Projects → XYZ ---
    for proj in raw.get("projects", []):
        source_text = " ".join(proj.get("bullets", [])) or proj.get("summary", "") or proj.get("title","")
        bullets = make_xyz_bullets(source_text, tools=proj.get("tools")) if source_text else []

        structured["projects"].append({
            "title": proj.get("title", ""),
            "tools": proj.get("tools", ""),
            "dates": proj.get("dates", proj.get("date", "")),
            "bullets": bullets[:2]  # cap at 2
        })

    # --- Extracurriculars → XYZ ---
    for ex in raw.get("extracurriculars", []):
        source_text = (
            " ".join(ex.get("bullets", []))
            or ex.get("summary", "")
            or ex.get("description", "")
            or ex.get("title","")
        )
        bullets = make_xyz_bullets(source_text, tools=None) if source_text else []

        structured["extracurriculars"].append({
            "title": ex.get("title", ""),
            "dates": ex.get("dates", ex.get("date", "")),
            "bullets": bullets[:2]
        })

    return structured

# --- dev-only quick test (optional) ---
# if __name__ == "__main__":
#     sample = {
#         "contact": {},
#         "education": [],
#         "skills": {},
#         "experience": [
#             {"title":"Web Developer","company":"Gabson Official","location":"Abuja","dates":"May 2025 – Present",
#              "summary":"Was responsible for creating and managing the company's website using Python and GitHub Actions. Collected user feedback and optimized pages."},
#         ],
#     }
#     out = build_resume(sample)
#     from pprint import pprint
#     pprint(out)
