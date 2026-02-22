# Post #2: Designing a Dataset for Flaky Test Prediction in CI/CD

## Hook
A flaky model is only as good as its dataset design. Feature engineering quality matters more than algorithm choice in early stages.

## What CI Logs Should Capture
- `test_name`, `run_id`, `timestamp`
- `pass_fail`, `retry_count`, `duration_ms`
- environment context (`browser`, `headless_mode`)
- optional stress signals (`cpu_load`, `memory_usage`, `network_latency`)

## Feature Strategy
Aggregate run-level logs into per-test features:
- behavior: `fail_rate`, `retry_rate`
- timing: `duration_mean_ms`, `duration_var_ms`, `p95_duration_ms`, `duration_cv`
- stability trend: `max_fail_streak`

## Labeling Instability
Operational label:
- `label_flaky = 1` when `0 < pass_rate < 1`
- `label_flaky = 0` otherwise

## Evidence in Repo
- Synthetic run logs: `data/processed/synthetic_ci_runs.csv`
- Feature builder: `feature_engineering/build_features.py`
- Feature table: `data/processed/sample_features.csv`
- Supporting table: `docs/post-02-feature-table.md`

## Reproducible Commands
```bash
python3 feature_engineering/generate_synthetic_logs.py --runs 80
python3 feature_engineering/build_features.py \
  --input data/processed/synthetic_ci_runs.csv \
  --output data/processed/sample_features.csv
```

## CTA
Which feature has been most useful for catching flaky behavior in your pipelines?
