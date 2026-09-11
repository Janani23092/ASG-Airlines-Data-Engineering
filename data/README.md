# Data handling

The public repository intentionally excludes the original source workbook and raw passenger/booking/payment extracts because they contain personal or sensitive-looking fields.

`data/sample/` contains a synthetic, structurally representative sample that can run the pipeline end-to-end. The competition source workbook can be supplied locally under `data/raw/UseCase_-_Airlines.xlsx` without committing it to GitHub.

The pipeline preserves raw inputs locally, validates records, quarantines hard failures, masks passenger/booking identifiers before analytics, and produces cleaned/curated outputs.
