from pathlib import Path
import pandas as pd

REQUIRED_SHEETS = ["flights", "bookings", "passengers", "payments"]

def load_source(workbook: str | Path):
    workbook = Path(workbook)
    if not workbook.exists():
        raise FileNotFoundError(f"Source workbook not found: {workbook}")
    xls = pd.ExcelFile(workbook)
    missing = [s for s in REQUIRED_SHEETS if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Missing required sheets: {missing}")
    return {s: pd.read_excel(xls, s) for s in REQUIRED_SHEETS}
