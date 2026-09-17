# Reproduce the baseline

From the repository root, install `python -m pip install -r requirements.txt`, then run `python scripts/verify_baseline.py`.

This trains the existing logistic-regression baseline from the included processed CSV without loading serialized models. Results are written to `reports/business/baseline_verification.json`.

The baseline uses an 80/20 stratified split. Existing imputation precedes splitting, so this is a reproducibility check, not proof of leakage-free generalization. Fit preprocessing on training folds before making production performance claims. This is a learning project, not a lending decision service.

See `reports/figures` for original analysis outputs. Tableau screenshots are available under `dashboard/screenshots`; the supplied workbook may require reconnecting its local data source.
