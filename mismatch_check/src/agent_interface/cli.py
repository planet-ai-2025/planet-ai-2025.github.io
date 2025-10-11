import argparse, json, os
from agent_interface.agent import TableCheckAgent
from agent_interface.tools import tool_extract_with_tesseract, tool_compare, compare_all_pages

def main():
    ap = argparse.ArgumentParser(description="Offline PDF↔CSV table checker (Tesseract OCR, multipage).")
    ap.add_argument("--image", help="PNG/JPG of PDF page")
    ap.add_argument("--pdf", help="PDF file")
    ap.add_argument("--page", type=int, default=1, help="1-based page index when --pdf is used")
    ap.add_argument("--all_pages", action="store_true", help="Process all pages of the PDF")
    ap.add_argument("--csv", required=True, help="Ground-truth CSV path")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--dpi", type=int, default=300, help="PDF rasterization DPI")
    ap.add_argument("--abs_tol", type=float, default=0.01, help="Absolute tolerance")
    ap.add_argument("--rel_tol", type=float, default=0.001, help="Relative tolerance")
    args = ap.parse_args()

    if not args.image and not args.pdf:
        ap.error("Provide --image or --pdf")

    if args.all_pages:
        if not args.pdf:
            ap.error("--all_pages requires --pdf")
        os.makedirs(args.out, exist_ok=True)
        compare_all_pages(args.pdf, args.csv, args.out, dpi=args.dpi, abs_tol=args.abs_tol, rel_tol=args.rel_tol)
        print(json.dumps({"status":"ok","mode":"all_pages","out": args.out}, indent=2))
        return

    tools = {"tesseract": tool_extract_with_tesseract, "compare": tool_compare}
    agent = TableCheckAgent(tools)

    spec = {
        "image": args.image,
        "pdf": args.pdf,
        "page": args.page,
        "csv": args.csv,
        "out": args.out,
        "dpi": args.dpi,
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol
    }
    result = agent.run_single(spec)
    print(json.dumps(result["summary"], indent=2))

if __name__ == "__main__":
    main()
