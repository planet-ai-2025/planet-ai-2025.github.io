import io, tempfile, re, os, json
from typing import Dict, Any, List, Optional
import pandas as pd
from pdf2image import convert_from_path
import pytesseract, cv2
from PIL import Image


def _page_to_pil(pdf_path: str, page: int, dpi: int = 300) -> Image.Image:
    pages = convert_from_path(pdf_path, dpi=dpi, first_page=page, last_page=page)
    if not pages:
        raise RuntimeError("PDF render failed; check page number")
    return pages[0].convert("RGB")


def _clean_number(s):
    if s is None: return None
    t = str(s).strip().replace(",", "").replace("$", "")
    if t.startswith("(") and t.endswith(")"):
        t = "-" + t[1:-1]
    t = re.sub(r"[^0-9\-\.\(\)]", "", t)
    try: return float(t) if t else None
    except: return None


def _values_match(a, b, abs_tol, rel_tol):
    if a is None or b is None: return False
    diff = abs(a-b)
    scale = max(abs(a), abs(b))
    return (diff <= abs_tol) or (diff <= rel_tol * (scale if scale>0 else 1.0))


def tool_extract_with_tesseract(args: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Load image (from file) or render PDF page to image
    if args.get("image"):
        pil_img = Image.open(args["image"]).convert("RGB")
    else:
        pil_img = _page_to_pil(args["pdf"], int(args.get("page", 1)), dpi=int(args.get("dpi", 300)))

    # Save to tmp to get a cv2 image for preprocessing
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    pil_img.save(tmp.name, format="PNG")

    img = cv2.imread(tmp.name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Simple binarization; you can swap for adaptive if needed
    _, binim = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    df = pytesseract.image_to_data(
        binim, lang="eng",
        config="--psm 6 --oem 3",
        output_type=pytesseract.Output.DATAFRAME
    )
    df = df[(df.conf != -1) & (df.text.astype(str).str.strip()!="")]
    if df.empty:
        return []

    # group tokens by rough rows using y-centers; then split into 4 columns by x-order buckets
    df["xc"] = df["left"] + df["width"]/2
    df["yc"] = df["top"] + df["height"]/2
    df = df.sort_values("yc")

    rows, cur, last_y = [], [], None
    for _, r in df.iterrows():
        if last_y is None or abs(r["yc"]-last_y) <= 0.6*r["height"]:
            cur.append(r); last_y = r["yc"] if last_y is None else 0.5*last_y+0.5*r["yc"]
        else:
            rows.append(pd.DataFrame(cur).sort_values("xc")); cur=[r]; last_y=r["yc"]
    if cur: rows.append(pd.DataFrame(cur).sort_values("xc"))

    table = []
    for rd in rows:
        order = rd["xc"].rank(method="first").astype(int).values
        num_cols = 4
        col_ids = ((order-1) * num_cols) // max(1, len(order))
        row = [""]*num_cols
        for (_, tok), cid in zip(rd.iterrows(), col_ids):
            if cid < num_cols:
                row[cid] = (row[cid] + " " + str(tok["text"]).strip()).strip()
        table.append(row)

    out = pd.DataFrame(table, columns=["id","qty","price","total"])
    for c in ["qty","price","total"]:
        out[c] = out[c].apply(_clean_number)
    # return list-of-dicts
    return out.to_dict(orient="records")


def tool_compare(args: Dict[str, Any]):
    csv_path = args["csv_path"]
    ocr_rows = args["ocr_rows"]
    out_dir = args.get("out_dir","report")
    abs_tol = float(args.get("abs_tol", 0.01))
    rel_tol = float(args.get("rel_tol", 0.001))
    page = args.get("page")  # optional page number for filenames

    os.makedirs(out_dir, exist_ok=True)
    src = pd.read_csv(csv_path)
    ocr = pd.DataFrame(ocr_rows)

    n = min(len(src), len(ocr))
    src = src.head(n).reset_index(drop=True)
    ocr = ocr.head(n).reset_index(drop=True)

    compare_cols = [c for c in ["qty","price","total"] if c in src.columns and c in ocr.columns]
    if not compare_cols:
        compare_cols = list(set(src.columns) & set(ocr.columns))

    records = []
    for c in compare_cols:
        for i in range(n):
            a, b = src.loc[i, c], ocr.loc[i, c]
            if isinstance(a, str): a = _clean_number(a)
            if isinstance(b, str): b = _clean_number(b)
            if not _values_match(a, b, abs_tol, rel_tol):
                records.append({"row": i, "column": c, "csv_value": a, "pdf_value": b,
                                "abs_diff": None if a is None or b is None else abs(a-b)})

    # Write outputs
    mm = pd.DataFrame(records) if records else pd.DataFrame([{ "message":"No mismatches beyond tolerance." }])
    if page is not None:
        out_dir_page = os.path.join(out_dir, f"page_{int(page)}")
        os.makedirs(out_dir_page, exist_ok=True)
        mm.to_csv(os.path.join(out_dir_page, "mismatches.csv"), index=False)
        ocr.to_csv(os.path.join(out_dir_page, "ocr_table.csv"), index=False)
        with open(os.path.join(out_dir_page, "summary.json"), "w") as f:
            json.dump({"rows_compared": int(n), "mismatch_count": 0 if records==[] else len(records),
                       "columns": compare_cols, "abs_tol": abs_tol, "rel_tol": rel_tol, "page": int(page)}, f, indent=2)
    else:
        mm.to_csv(f"{out_dir}/mismatches.csv", index=False)
        ocr.to_csv(f"{out_dir}/ocr_table.csv", index=False)
        with open(f"{out_dir}/summary.json","w") as f:
            json.dump({"rows_compared": int(n), "mismatch_count": 0 if records==[] else len(records),
                       "columns": compare_cols, "abs_tol": abs_tol, "rel_tol": rel_tol}, f, indent=2)

    return {"rows_compared": int(n), "mismatch_count": 0 if records==[] else len(records)}


def compare_all_pages(pdf_path: str, csv_path: str, out_dir: str, dpi: int = 300, abs_tol: float = 0.01, rel_tol: float = 0.001):
    os.makedirs(out_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=dpi)
    all_ocr = []
    all_mm = []
    for idx, page_img in enumerate(pages, start=1):
        # Save each page to temp and reuse the existing single-page flow
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        page_img.save(tmp.name, 'PNG')
        rows = tool_extract_with_tesseract({"image": tmp.name})
        # write per-page outputs via tool_compare (so formats match)
        tool_compare({
            "csv_path": csv_path,
            "ocr_rows": rows,
            "out_dir": out_dir,
            "abs_tol": abs_tol,
            "rel_tol": rel_tol,
            "page": idx,
        })
        # For aggregation
        for r in rows:
            r = dict(r)
            r["page"] = idx
            all_ocr.append(r)
        # Read back mismatches to aggregate
        mm_path = os.path.join(out_dir, f"page_{idx}", "mismatches.csv")
        try:
            mm_df = pd.read_csv(mm_path)
            if not mm_df.empty and 'message' not in mm_df.columns:
                mm_df["page"] = idx
                all_mm.append(mm_df)
        except Exception:
            pass

    if all_ocr:
        pd.DataFrame(all_ocr).to_csv(os.path.join(out_dir, "ocr_all_pages.csv"), index=False)
    if all_mm:
        pd.concat(all_mm, ignore_index=True).to_csv(os.path.join(out_dir, "mismatches_all_pages.csv"), index=False)
