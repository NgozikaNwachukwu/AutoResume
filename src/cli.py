"""CLI to generate a resume PDF from JSON input."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from builder import build_resume
from pdf_generator import generate_pdf

logger = logging.getLogger(__name__)


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
    # If generate_pdf expects a string path, cast to str for safety.
    generate_pdf(resume, str(output_path))

    logger.info("Wrote %s", output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
