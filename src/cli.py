"""CLI to generate a resume PDF from JSON input (robust import)."""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import logging
from pathlib import Path

from src.builder import build_resume

logger = logging.getLogger(__name__)


def _resolve_pdf_callable():
    """
    Find a callable in src.pdf_generator that can produce a PDF.
    Tries common func names; falls back to PDFGenerator class.
    """
    mod = importlib.import_module("src.pdf_generator")

    for name in ("generate_pdf", "create_pdf", "write_pdf", "build_pdf", "render_pdf"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn

    cls = getattr(mod, "PDFGenerator", None)
    if cls is not None:
        inst = cls()
        if callable(getattr(inst, "generate", None)):
            return lambda resume, out: inst.generate(resume, out)
        if callable(getattr(inst, "build", None)):
            return lambda resume, out: inst.build(resume, out)

    public = [n for n in dir(mod) if not n.startswith("_")]
    raise RuntimeError(
        "Could not find a PDF writer in src.pdf_generator. "
        f"Tried common names and PDFGenerator. Available: {public}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate resume PDF from JSON")
    parser.add_argument("--input", required=True, help="Path to raw JSON data")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with input_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    resume = build_resume(raw)
    pdf_callable = _resolve_pdf_callable()

    sig = inspect.signature(pdf_callable)
    try:
        if len(sig.parameters) >= 2:
            pdf_callable(resume, str(output_path))
        else:
            pdf_bytes = pdf_callable(resume)
            output_path.write_bytes(pdf_bytes)
    except TypeError:
        try:
            pdf_callable(resume, str(output_path))
        except TypeError:
            pdf_bytes = pdf_callable(resume)
            output_path.write_bytes(pdf_bytes)

    logger.info("Wrote %s", output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
