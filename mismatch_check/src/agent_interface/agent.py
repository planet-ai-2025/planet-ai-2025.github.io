from typing import Dict, Any

class TableCheckAgent:
    """
    Offline agent facade. Delegates to Tesseract extractor and comparator.
    """
    def __init__(self, tools: Dict[str, callable]):
        # expects keys: "tesseract", "compare"
        self.tools = tools

    def run_single(self, spec: Dict[str, Any]):
        rows = self.tools["tesseract"]({
            "image": spec.get("image"),
            "pdf": spec.get("pdf"),
            "page": spec.get("page", 1),
            "dpi": spec.get("dpi", 300),
        })
        summary = self.tools["compare"]({
            "csv_path": spec["csv"],
            "ocr_rows": rows,
            "out_dir": spec.get("out", "report"),
            "abs_tol": spec.get("abs_tol", 0.01),
            "rel_tol": spec.get("rel_tol", 0.001),
            "page": spec.get("page"),
        })
        return {"ocr_rows": rows, "summary": summary}
