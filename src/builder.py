# ======================
# src/builder.py
# ======================

# --- deps: auto-install + data check ---
# Auto-install nltk if missing (safer subprocess form)
try:
    import nltk
except ModuleNotFoundError:
    # CHANGE: prefer subprocess over os.system (more reliable, cross-platform)
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    import nltk

import re

# Auto-download required NLTK resources if missing (first run only)
def _ensure_nltk_data():
    required = {
        "tokenizers": ["punkt", "punkt_tab"],               # CHANGE: include punkt_tab (newer NLTK needs it)
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
# Phase 2: Rewrite helpers
# =========================

# Strong verbs to anchor bullet openings/promotions
ACTION_VERBS = {
    "built","created","developed","implemented","designed","automated","tested",
    "led","migrated","optimized","configured","fixed","integrated","deployed",
    "refactored","improved","reduced","increased","coordinated","collaborated",
    "managed","launched","delivered","orchestrated","owned","enhanced"
}

# CHANGE: expand weak intros we strip out
WEAK_PREFIXES = [
    r"i\s+(was\s+)?(responsible\s+for|tasked\s+with|tasked\s+to)\s+",
    r"i\s+(helped|assisted)\s+to\s+",
    r"i\s+(helped|assisted)\s+",
    r"\bwe\s+",
    r"my role (was|included)\s+",
    r"\bi\s+was\s+in\s+charge\s+of\s+",
]

# CHANGE: add more passive→active normalizations
PASSIVE_TO_ACTIVE = [
    (r"\bwas\b\s+(tested|built|created|developed|implemented|designed|managed)\b", r"\1"),
    (r"\bwere\b\s+(tested|built|created|developed|implemented|designed|managed)\b", r"\1"),
]

# Detect a trailing tech/tools clause (“using/with/in/via/through …”)
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
        tl = t.lower()
        if tl in {
            "python","java","javascript","typescript","docker","kubernetes","git",
            "github","flask","django","react","azure","aws","gcp","sql","jenkins",
            "github actions","command line","cli"
        }:
            # CHANGE: special-casing a few multi-word tech labels
            if tl == "github actions":
                tech.append("GitHub Actions")
            elif tl == "command line" or tl == "cli":
                tech.append("command line")
            else:
                tech.append(t.capitalize())
        else:
            tech.append(t)
    return ", ".join([x for x in tech if x])

def _has_number(s: str) -> bool:
    return bool(re.search(r"\b\d+%?|\b\d+\b", s))

# CHANGE: simple gerund→past converter for leading verbs (creating→created)
def _gerund_to_past(word: str) -> str:
    base = re.sub(r"ing$", "", word)
    if not base:
        return word
    if base.endswith("y"):
        return base[:-1] + "ied"
    if base.endswith("e"):
        return base + "d"
    return base + "ed"

# CHANGE: promote “(I/we) was/were tasked with|to <gerund> …” → “<Verb-ed> …”
def _promote_tasked_phrases(s: str) -> str:
    # remove explicit “I/We was|were tasked …”
    s = re.sub(r"^(i|we)\s+(was|were)\s+tasked\s+(with|to)\s+", "", s, flags=re.I)
    s = re.sub(r"^was\s+tasked\s+(with|to)\s+", "", s, flags=re.I)
    # convert initial gerund to past (“creating …” → “Created …”)
    m = re.match(r"^([a-z]+)ing\b(.*)$", s, flags=re.I)
    if m:
        first = _gerund_to_past(m.group(1)).capitalize()
        rest = m.group(2)
        s = f"{first}{rest}"
    return s

# CHANGE: collapse repeated gerunds (“…, managing …, managing …” → “…, managing … and …”)
def _dedupe_repeated_gerunds(s: str) -> str:
    s = re.sub(r"\b,\s*managing\b\s+", " and ", s, flags=re.I)
    s = re.sub(r"\b,\s*creating\b\s+", " and ", s, flags=re.I)
    return s

def _strong_opening(s: str) -> str:
    s = s.strip()
    s = _promote_tasked_phrases(s)            # CHANGE: handle “was tasked …”
    s = re.sub(r"^(i|we)\s+", "", s, flags=re.I)
    for pat in WEAK_PREFIXES:
        s = re.sub(pat, "", s, flags=re.I)
    for pat, rep in PASSIVE_TO_ACTIVE:
        s = re.sub(pat, rep, s, flags=re.I)
    s = _dedupe_repeated_gerunds(s)           # CHANGE: clean repeated gerunds

    # Promote an action verb to the front if first word is weak
    words = s.split()
    if words:
        first = words[0].lower()
        if first not in ACTION_VERBS:
            m = re.search(r"\b(" + "|".join(ACTION_VERBS) + r")\b", s, flags=re.I)
            if m:
                verb = m.group(1)
                s = verb.capitalize() + " " + re.sub(
                    r".*?\b" + re.escape(verb) + r"\b", "", s, count=1, flags=re.I
                ).strip()
    return s[0:1].upper() + s[1:] if s else s

# CHANGE: main rewriter now *removes* the old metric placeholder – no more “(+ impact: add metric)”
def rewrite_to_resume_bullets(summary: str) -> list[str]:
    """Turn raw multi-sentence text into polished resume bullets."""
    from nltk.tokenize import sent_tokenize
    bullets = []
    for sent in sent_tokenize(summary or ""):
        sent = _clean_sentence(sent)
        if not sent:
            continue

        # Extract trailing tools/tech (“using/with/in/via/through …”)
        tech = None
        m = re.search(TECH_SPLIT, sent, flags=re.I)
        if m:
            tech = _capitalize_tech(m.group(1))
            sent = sent[:m.start()].strip()

        sent = _strong_opening(sent)

        # Build final bullet text (no metric placeholder)
        core = sent
        if tech:
            core = f"{core} using {tech}"

        bullets.append("• " + core.rstrip(".") + ".")

    # De-dup and cap at 4 bullets
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
# Main builder function
# =========================
def build_resume(raw: dict) -> dict:
    """
    Turn raw input from questions.py into structured, bullet-ready data for the PDF.
    """
    structured = {
        "contact": raw.get("contact", {}),
        "education": raw.get("education", []),
        "skills": raw.get("skills", {}),
        "experience": [],
        "projects": [],
        "extracurriculars": []
    }

    # Experiences → rewrite bullets
    for exp in raw.get("experience", []):
        summary = (exp.pop("summary", "") or "").strip()
        bullets = rewrite_to_resume_bullets(summary) if summary else []
        structured["experience"].append({
            "title": exp.get("title", ""),
            "company": exp.get("company", ""),
            "location": exp.get("location", ""),
            "dates": exp.get("dates", exp.get("date", "")),
            "bullets": bullets
        })

    # Projects → rewrite bullets
    for proj in raw.get("projects", []):
        summary = (proj.pop("summary", "") or "").strip()
        bullets = rewrite_to_resume_bullets(summary) if summary else []
        structured["projects"].append({
            "title": proj.get("title", ""),
            "tools": proj.get("tools", ""),
            "dates": proj.get("dates", proj.get("date", "")),
            "bullets": bullets
        })

    # Extracurriculars → rewrite bullets
    for ex in raw.get("extracurriculars", []):
        # support either 'description' or 'summary'
        summary = (ex.pop("description", "") or ex.pop("summary", "") or "").strip()
        bullets = rewrite_to_resume_bullets(summary) if summary else []
        structured["extracurriculars"].append({
            "title": ex.get("title", ""),
            "dates": ex.get("dates", ex.get("date", "")),
            "bullets": bullets
        })

    return structured

# --- dev-only quick test (optional) ---
if __name__ == "__main__":
    sample = {
        "contact": {},
        "education": [],
        "skills": {},
        "experience": [
            {"title":"Webdev","company":"Gabson Official","location":"Abuja","dates":"May 2025 – Present",
             "summary":"I was tasked with creating and managing the company's website."},
            {"title":"Social Media Manager","company":"Dalema Supermarket","location":"Abuja/Kaduna","dates":"Jun 2025 – Present",
             "summary":"I was tasked using creating the company's social media, managing online presence."},
        ],
        "projects": [
            {"title":"AutoResume CLI","tools":"Python","dates":"Aug 2025 – Present",
             "summary":"I was primarily tasked using testing the program at every step before deployment in python, command line."}
        ],
        "extracurriculars": [
            {"title":"Hiclub","dates":"Nov 2021 – Aug 2022",
             "description":"Co-founded the club, primarily using the mission to teach young girls, bring them into the tech space."}
        ]
    }
    out = build_resume(sample)
    from pprint import pprint
    pprint(out)
