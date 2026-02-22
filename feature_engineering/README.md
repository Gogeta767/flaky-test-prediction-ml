# Feature Engineering

Scripts in this folder will transform raw CI/test execution logs into model-ready features.

## Scripts

- `generate_synthetic_logs.py`: creates reproducible run-level synthetic CI logs.
- `build_features.py`: aggregates run-level logs into per-test features and flaky labels.

## Usage

```bash
python3 feature_engineering/generate_synthetic_logs.py --runs 80
python3 feature_engineering/build_features.py \
  --input data/processed/synthetic_ci_runs.csv \
  --output data/processed/sample_features.csv
```
