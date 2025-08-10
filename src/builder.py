# --- deps: auto-install + data check ---
# Auto-install nltk if missing
try:
    import nltk
except ModuleNotFoundError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    import nltk

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
# Phase 2: Rewrite helpers
# =========================
ACTION_VERBS = {
    "built","created","developed","implemented","designed","automated","tested",
    "led","migrated","optimized","configured","fixed","integrated","deployed",
    "refactored","improved","reduced","increased","coordinated","collaborated"
}
WEAK_PREFIXES = [
    r"i\s+(was\s+)?(responsible\s+for|tasked\s+with)\s+",
    r"i\s+(helped|assisted)\s+to\s+",
    r"i\s+(helped|assisted)\s+",
    r"we\s+",
    r"my role (was|included)\s+",
]
PASSIVE_TO_ACTIVE = [
    (r"\bwas\b\s+(tested|built|created|developed|implemented|designed)\b", r"\1"),
    (r"\bwere\b\s+(tested|built|created|developed|implemented|designed)\b", r"\1"),
]
TECH_SPLIT = r"(?:using|with|in|via|through)\s+(.+)$"

def _clean_sentence(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".")
    return s

def _capitalize_tech(s: str) -> str:
    tech = []
    for t in re.split(r"\s*,\s*|\s+and\s+", s):
        t = t.strip()
        if t.lower() in {
            "python","java","javascript","typescript","docker","kubernetes","git",
            "github","flask","django","react","azure","aws","gcp","sql"
        }:
            tech.append(t.capitalize())
        else:
            tech.append(t)
    return ", ".join(tech)

def _has_number(s: str) -> bool:
    return bool(re.search(r"\b\d+%?|\b\d+\b", s))

def _strong_opening(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^(i|we)\s+", "", s, flags=re.I)
    for pat in WEAK_PREFIXES:
        s = re.sub(pat, "", s, flags=re.I)
    for pat, rep in PASSIVE_TO_ACTIVE:
        s = re.sub(pat, rep, s, flags=re.I)
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

def rewrite_to_resume_bullets(summary: str) -> list[str]:
    """Turn raw multi-sentence text into polished resume bullets."""
    from nltk.tokenize import sent_tokenize
    bullets = []
    for sent in sent_tokenize(summary or ""):
        sent = _clean_sentence(sent)
        if not sent:
            continue

        # extract tools/tech at the end (after 'using/with/in/via/through ...')
        tech = None
        m = re.search(TECH_SPLIT, sent, flags=re.I)
        if m:
            tech = _capitalize_tech(m.group(1))
            sent = sent[:m.start()].strip()

        sent = _strong_opening(sent)

        core = sent
        if tech:
            core = f"{core} using {tech}"

        # add a gentle metric placeholder only if no numbers present
        if not _has_number(core):
            core = f"{core} (+ impact: add metric)"

        bullets.append("• " + core + ".")

    # de-dup and cap at 4 bullets
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
            "dates": exp.get("dates", ""),
            "bullets": bullets
        })

    # Projects → rewrite bullets (XYZ-ish)
    for proj in raw.get("projects", []):
        summary = (proj.pop("summary", "") or "").strip()
        bullets = rewrite_to_resume_bullets(summary) if summary else []
        structured["projects"].append({
            "title": proj.get("title", ""),
            "tools": proj.get("tools", ""),
            "dates": proj.get("dates", ""),
            "bullets": bullets
        })

    # Extracurriculars → rewrite bullets
    for ex in raw.get("extracurriculars", []):
        # some of your data uses 'description' vs 'summary'
        summary = (ex.pop("description", "") or ex.pop("summary", "") or "").strip()
        bullets = rewrite_to_resume_bullets(summary) if summary else []
        structured["extracurriculars"].append({
            "title": ex.get("title", ""),
            "dates": ex.get("dates", ""),
            "bullets": bullets
        })

    return structured

# --- dev-only test (optional) ---
if __name__ == "__main__":
    sample = {
        "contact": {},
        "education": [],
        "skills": {},
        "experience": [
            {"title":"QA Intern","company":"Crest","location":"Hybrid","dates":"Aug 2025 – Present",
             "summary":"I was responsible for testing the program before deployment using Python and Git. I collaborated with devs to fix issues."}
        ],
        "projects": [
            {"title":"AutoResume","tools":"Python, NLTK","dates":"2025","summary":"I built an auto resume tool in python and docker to help students."}
        ],
        "extracurriculars": [
            {"title":"Women in Engineering","dates":"2024 – Present","description":"I organized events and mentored first-years in the club."}
        ]
    }
    out = build_resume(sample)
    from pprint import pprint
    pprint(out)
