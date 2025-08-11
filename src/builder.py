# ======================
# src/builder.py
# ======================

# --- deps: auto-install + data check ---
try:
    import nltk
except ModuleNotFoundError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    import nltk

import re
import copy

def _ensure_nltk_data():
    required = {
        "tokenizers": ["punkt", "punkt_tab"],   # punkt_tab for newer NLTK
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

ACTION_VERBS = {
    "built","created","developed","implemented","designed","automated","tested",
    "led","migrated","optimized","configured","fixed","integrated","deployed",
    "refactored","improved","reduced","increased","coordinated","collaborated",
    "managed","launched","delivered","orchestrated","owned","enhanced",
    "collected","analyzed","maintained","monitored","supported","documented","validated",
    "taught","grew"
}

WEAK_PREFIXES = [
    r"i\s+(was\s+)?(responsible\s+for|tasked\s+with|tasked\s+to)\s+",
    r"(?:was|were)\s+responsible\s+for\s+",          # handles "Was responsible for ..."
    r"i\s+(helped|assisted)\s+to\s+",
    r"i\s+(helped|assisted)\s+",
    r"\bwe\s+",
    r"my role (was|included)\s+",
    r"\bi\s+was\s+in\s+charge\s+of\s+",
]

PASSIVE_TO_ACTIVE = [
    (r"\bwas\b\s+(tested|built|created|developed|implemented|designed|managed)\b", r"\1"),
    (r"\bwere\b\s+(tested|built|created|developed|implemented|designed|managed)\b", r"\1"),
]

TECH_SPLIT = r"(?:using|with|in|via|through)\s+(.+)$"

_TECH_MAP = {
    "python":"Python","java":"Java","javascript":"JavaScript","typescript":"TypeScript",
    "docker":"Docker","kubernetes":"Kubernetes","git":"Git","github":"GitHub",
    "flask":"Flask","django":"Django","react":"React","azure":"Azure","aws":"AWS","gcp":"GCP",
    "sql":"SQL","mysql":"MySQL","jenkins":"Jenkins","pandas":"Pandas","numpy":"NumPy",
    "pytest":"pytest","selenium":"Selenium","html":"HTML","css":"CSS","github actions":"GitHub Actions",
    "cli":"command line","command line":"command line"
}

def _normalize_tech_in_text(s: str) -> str:
    for k, v in _TECH_MAP.items():
        s = re.sub(rf"\b{re.escape(k)}\b", v, s, flags=re.I)
    return s

def _clean_sentence(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".")
    return s

def _capitalize_tech(s: str) -> str:
    tech = []
    for t in re.split(r"\s*,\s*|\s+and\s+", s):
        t = t.strip()
        if not t:
            continue
        tech.append(_TECH_MAP.get(t.lower(), t.capitalize() if len(t) > 1 else t))
    return ", ".join([x for x in tech if x])

# --- irregular past (fixes "Teached" -> "Taught") ---
IRREGULAR_PAST = {
    "teach":"taught","lead":"led","build":"built","make":"made","write":"wrote",
    "run":"ran","grow":"grew","bring":"brought","buy":"bought","catch":"caught",
    "think":"thought","seek":"sought","fight":"fought","sell":"sold","hold":"held",
    "keep":"kept","leave":"left","meet":"met","pay":"paid","say":"said","see":"saw",
    "take":"took","come":"came","go":"went"
}
def _to_past(word: str) -> str:
    w = word.lower()
    if w in IRREGULAR_PAST:
        return IRREGULAR_PAST[w]
    if w.endswith("y"):
        return w[:-1] + "ied"
    if w.endswith("e"):
        return w + "d"
    return w + "ed"

def _promote_tasked_phrases(s: str) -> str:
    s = re.sub(r"^(i|we)\s+(was|were)\s+tasked\s+(with|to)\s+", "", s, flags=re.I)
    s = re.sub(r"^was\s+tasked\s+(with|to)\s+", "", s, flags=re.I)
    m = re.match(r"^([a-z]+)ing\b(.*)$", s, flags=re.I)
    if m:
        first = _to_past(m.group(1)).capitalize()
        rest = m.group(2)
        s = f"{first}{rest}"
    return s

def _dedupe_repeated_gerunds(s: str) -> str:
    s = re.sub(r"\b,\s*managing\b\s+", " and ", s, flags=re.I)
    s = re.sub(r"\b,\s*creating\b\s+", " and ", s, flags=re.I)
    return s

def _strong_opening(s: str) -> str:
    s = s.strip()
    s = _promote_tasked_phrases(s)
    s = re.sub(r"^(was|were)\s+", "", s, flags=re.I)  # drop naked auxiliaries
    s = re.sub(r"^(i|we)\s+", "", s, flags=re.I)      # drop pronouns
    for pat in WEAK_PREFIXES:
        s = re.sub(pat, "", s, flags=re.I)
    for pat, rep in PASSIVE_TO_ACTIVE:
        s = re.sub(pat, rep, s, flags=re.I)
    s = _dedupe_repeated_gerunds(s)

    m = re.match(r"^([A-Za-z]+)ing\b(.*)$", s)        # creating → Created
    if m:
        s = _to_past(m.group(1)).capitalize() + m.group(2)

    words = s.split()
    if words and words[0].lower() not in ACTION_VERBS:
        m = re.search(r"\b(" + "|".join(ACTION_VERBS) + r")\b", s, flags=re.I)
        if m:
            verb = m.group(1)
            s = verb.capitalize() + " " + re.sub(
                r".*?\b" + re.escape(verb) + r"\b", "", s, count=1, flags=re.I
            ).strip()

    # If we still didn't land on a verb-led opening, use a neutral "Delivered ..."
    if not re.match(r"^(" + "|".join(ACTION_VERBS) + r")\b", s, flags=re.I):
        s = "Delivered " + s

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
        b = "• " + core.rstrip(".") + "."
        bullets.append(_normalize_tech_in_text(b))
    # dedupe and cap
    seen, final = set(), []
    for b in bullets:
        k = b.lower()
        if k not in seen:
            seen.add(k); final.append(b)
        if len(final) == 4: break
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

def _pick_impact(text: str) -> str:
    t = (text or "").lower()
    if any(w in t for w in ["test","qa","pytest","selenium","coverage","unit"]):
        return "increasing test coverage"
    if any(w in t for w in ["website","page","ui","ux","portfolio"]):
        return "enhancing usability"
    if "social" in t or "engagement" in t or "content" in t:
        return "improving audience engagement"
    if any(w in t for w in ["pipeline","deploy","github actions","jenkins","automation","cli","script"]):
        return "reducing manual effort"
    return "improving reliability"

def _tools_phrase_for(val):
    if not val:
        return ""
    if isinstance(val, str):
        cleaned = _capitalize_tech(val)
    else:
        cleaned = _capitalize_tech(", ".join([str(x) for x in val if x]))
    return f" using {cleaned}" if cleaned else ""

def make_star_bullets(summary: str, role: str = "", org: str = "", tools=None) -> list[str]:
    from nltk.tokenize import sent_tokenize
    sents = [_clean_sentence(s) for s in sent_tokenize(summary or "") if _clean_sentence(s)]
    joined = " ".join(sents)

    task = sents[0] if sents else (role or "key responsibilities")
    b1 = "• " + _normalize_tech_in_text(_strong_opening(task).rstrip(".") + ".")
    action = sents[1] if len(sents) > 1 else "Implemented improvements"
    b2_core = _strong_opening(action) + _tools_phrase_for(tools)
    b2 = "• " + _normalize_tech_in_text(b2_core.rstrip(".") + ".")
    res = _pick_impact(joined + " " + (tools or ""))
    b3 = "• " + _normalize_tech_in_text(("Delivered measurable outcomes by " + res).rstrip(".") + ".")
    return [b1, b2, b3]

def make_xyz_bullets(summary: str, tools=None, max_bullets: int = 2) -> list[str]:
    from nltk.tokenize import sent_tokenize
    sents = [_clean_sentence(s) for s in sent_tokenize(summary or "") if _clean_sentence(s)]
    if not sents:
        return []

    what = _strong_opening(sents[0])                         # e.g., "Taught female students ..."
    how  = _strong_opening(sents[1]) if len(sents) > 1 else "implementing core features and tests"
    how  = re.sub(r"^(?:by\s+)", "", how, flags=re.I)        # avoid "by by"
    impact = _pick_impact(what + " " + how)

    b1 = f"• {what} by {how}{_tools_phrase_for(tools)}, {impact}."
    bullets = [_normalize_tech_in_text(b1)]

    for d in sents[2:][:max(0, max_bullets - 1)]:
        bullets.append(_normalize_tech_in_text("• " + _strong_opening(d).rstrip(".") + "."))

    return bullets[:max_bullets]

# =========================
# Utilities
# =========================

def _normalize_date_range(s: str) -> str:
    if not s:
        return s
    s = re.sub(r"\s*,\s*", " ", s)               # "Jun,2025" -> "Jun 2025"
    s = re.sub(r"\s*[-–—]\s*", " – ", s)         # normalize dash to en dash
    s = re.sub(r"\bpresent\b", "Present", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s

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
            "dates": _normalize_date_range(exp.get("dates", exp.get("date", ""))),
            "bullets": bullets[:3]
        })

    # --- Projects → XYZ ---
    for proj in raw.get("projects", []):
        source_text = " ".join(proj.get("bullets", [])) or proj.get("summary", "") or proj.get("title","")
        bullets = make_xyz_bullets(source_text, tools=proj.get("tools")) if source_text else []

        structured["projects"].append({
            "title": proj.get("title", ""),
            "tools": proj.get("tools", ""),
            "dates": _normalize_date_range(proj.get("dates", proj.get("date", ""))),
            "bullets": bullets[:2]
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
            "dates": _normalize_date_range(ex.get("dates", ex.get("date", ""))),
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
