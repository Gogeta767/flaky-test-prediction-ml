# Models

Training, evaluation, and model artifact scripts for flaky test prediction.

## Scripts

- `train_baselines.py`: trains Logistic Regression and Random Forest on a reproducible synthetic feature dataset and writes metrics.
- `evaluate.py`: prints threshold-oriented comparison from the metrics artifact.

## Usage

```bash
python3 models/train_baselines.py --samples 1200
python3 models/evaluate.py --metrics models/results/baseline_metrics.json
```

## Output

- `models/results/baseline_metrics.json`
