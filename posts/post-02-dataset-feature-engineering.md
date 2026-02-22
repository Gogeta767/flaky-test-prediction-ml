# Post #2: Designing a Dataset for Flaky Test Prediction in CI/CD

## What CI Logs Contain
- Test id/name
- Run id and timestamp
- Pass/fail outcome
- Retry count
- Duration
- Environment/browser context

## Feature Extraction Strategy
Engineer per-test aggregate features over historical windows.

## Labeling Instability
Label a test as flaky when it both passes and fails across repeated runs under unchanged code.

## Sample Feature Table
| test_name | fail_rate | retry_rate | duration_var | label_flaky |
|---|---:|---:|---:|---:|
| checkout.spec::payment | 0.32 | 0.28 | 0.41 | 1 |
| auth.spec::login | 0.00 | 0.00 | 0.03 | 0 |

## Python Snippet
```python
features["fail_rate"] = 1.0 - grouped["passed"].mean()
features["retry_rate"] = grouped["retry_count"].mean()
features["duration_var"] = grouped["duration_ms"].var().fillna(0.0)
```
