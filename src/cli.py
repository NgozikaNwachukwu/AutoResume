import argparse, json
from builder import build_resume
from pdf_generator import generate_pdf

def main():
    p = argparse.ArgumentParser(description="Generate resume PDF from JSON")
    p.add_argument("--input", required=True, help="Path to raw JSON data")
    p.add_argument("--output", required=True, help="Output PDF path")
    args = p.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    resume = build_resume(raw)
    generate_pdf(resume, args.output)
    print(f"✅ Wrote {args.output}")

if __name__ == "__main__":
    main()
