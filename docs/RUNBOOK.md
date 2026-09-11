# Runbook

## Local setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
pytest -q
```

The default run uses the synthetic sample workbook in `data/sample/`. For the competition source, place the original workbook locally at `data/raw/UseCase_-_Airlines.xlsx` and update the `SOURCE` setting in `run_pipeline.py`; do not commit that raw folder.
