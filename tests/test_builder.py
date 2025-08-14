import re
from builder import build_resume, rewrite_to_resume_bullets


def test_rewrite_makes_strong_bullets():
    summary = "I was tasked with creating the site using python. delivered outcomes."
    bullets = rewrite_to_resume_bullets(summary)
    assert bullets, "Should produce at least one bullet"
    assert all(b.startswith("• ") and b.rstrip().endswith(".") for b in bullets)


def test_build_resume_includes_gpa(sample_raw):
    out = build_resume(sample_raw)
    edu = out["education"][0]
    assert "GPA" in str(edu)


def test_experience_bullets_not_starting_with_i(sample_raw):
    out = build_resume(sample_raw)
    bullets = out["experience"][0]["bullets"]
    assert bullets, "Experience bullets should not be empty"
    assert not any(re.match(r"•\s*i\b", b, flags=re.I) for b in bullets)
