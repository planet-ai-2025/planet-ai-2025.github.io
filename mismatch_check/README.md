## Install

```bash
cd mismatch_check
python -m venv venv && source venv/bin/activate   # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# System deps:
#  - Tesseract OCR       (macOS: brew install tesseract; Ubuntu: sudo apt-get install tesseract-ocr)
#  - Poppler (pdf2image) (macOS: brew install poppler; Ubuntu: sudo apt-get install poppler-utils)
```

## Usage

### Single image input
```bash
export PYTHONPATH="$(pwd)/src"   # Windows PowerShell: $env:PYTHONPATH = "$pwd\src"
python -m agent_interface.cli --image data/sample_page.png --csv data/sample.csv --out report
```

### Single PDF page
```bash
export PYTHONPATH="$(pwd)/src"
python -m agent_interface.cli --pdf your.pdf --page 1 --csv data/sample.csv --out report --dpi 300
```

### All PDF pages
```bash
export PYTHONPATH="$(pwd)/src"
python -m agent_interface.cli --pdf your.pdf --all_pages --csv data/sample.csv --out report --dpi 300
```
This will create per‑page outputs under `report/page_1/`, `report/page_2/`, … and two aggregate files:
- `report/ocr_all_pages.csv`
- `report/mismatches_all_pages.csv`

## Outputs
Each run writes:
- `ocr_table.csv` — extracted rows (id, qty, price, total)
- `mismatches.csv` — rows/columns outside tolerance
- `summary.json` — rows compared, mismatch count, tolerances
(When `--all_pages` is used, these appear per page and also in aggregated CSVs.)

## Notes
- The table detection is heuristic; complex layouts may need cropping as preprocessing.
- Defaults: abs_tol=0.01, rel_tol=0.001.
