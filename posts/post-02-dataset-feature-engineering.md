# Post #2: Designing a Dataset for Flaky Test Prediction in CI/CD

## What CI Logs Contain
For flaky prediction, each run-level record should capture:

- `test_name`
- `run_id` and `timestamp`
- `pass_fail`
- `retry_count`
- `duration_ms`
- environment fields (`browser`, `headless_mode`)
- optional stress signals (`cpu_load`, `memory_usage`, `network_latency`)

In this repo, run-level data is produced at:

- `data/processed/synthetic_ci_runs.csv`

## Feature Extraction Strategy
Aggregate historical runs per test case into model-ready features. Current feature builder:

- Script: `feature_engineering/build_features.py`
- Output: `data/processed/sample_features.csv`

Core features:

- `fail_rate` and `pass_rate`
- `retry_rate`
- `duration_mean_ms`, `duration_var_ms`, `p95_duration_ms`
- `duration_cv`
- `max_fail_streak`
- optional load/latency means

## Labeling Instability
Use an operational flaky label from repeated runs under unchanged code:

- `label_flaky = 1` if `0 < pass_rate < 1`
- `label_flaky = 0` otherwise

This avoids manual labeling and aligns with common flaky-test definitions.

## Sample Feature Table
| test_name | fail_rate | retry_rate | duration_var_ms | label_flaky |
|---|---:|---:|---:|---:|
| notifications.spec::websocket_push | 0.3750 | 0.2125 | 14103.71 | 1 |
| checkout.spec::payment_flow | 0.3375 | 0.1125 | 13951.82 | 1 |
| auth.spec::login_success | 0.0000 | 0.0000 | 5395.66 | 0 |

## Python Snippet
```python
features["fail_rate"] = 1.0 - features["pass_rate"]
features["duration_cv"] = features["duration_std_ms"] / features["duration_mean_ms"]
features["label_flaky"] = ((features["pass_rate"] > 0.0) & (features["pass_rate"] < 1.0)).astype(int)
```

## Reproducible Commands
```bash
python3 feature_engineering/generate_synthetic_logs.py --runs 80
python3 feature_engineering/build_features.py \
  --input data/processed/synthetic_ci_runs.csv \
  --output data/processed/sample_features.csv
```
