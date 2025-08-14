from builder import build_resume
from pdf_generator import build_pdf
import os


def test_build_pdf_writes_file(tmp_path, sample_raw):
    structured = build_resume(sample_raw)
    out = tmp_path / "Resume.pdf"
    pdf_path = build_pdf(structured, filename=str(out))
    assert os.path.exists(pdf_path), "PDF file was not created"
    assert os.path.getsize(pdf_path) > 0, "PDF seems empty"
