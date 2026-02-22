# Post #3: Evaluating Machine Learning Models for Flaky Test Detection

## Models Compared
- Logistic Regression
- Random Forest

## Why Simple Models Can Win
For tabular CI features and limited data, linear models can be easier to calibrate and explain.

In this repo:

- Training script: `models/train_baselines.py`
- Evaluation summary: `models/evaluate.py`
- Metrics artifact: `models/results/baseline_metrics.json`

## Precision vs Recall in CI
- Higher precision reduces unnecessary retries/quarantine.
- Higher recall catches more flaky tests but can increase false positives.

## CI Trade-off
Tune thresholds based on pipeline cost of false positives versus false negatives.

From current baseline run:

- Logistic Regression (`t=0.50`): precision `0.686`, recall `0.641`
- Random Forest (`t=0.50`): precision `0.668`, recall `0.746`
- Logistic Regression (`t=0.70`): precision `0.839`, recall `0.260`

This is why threshold policy matters more than a single default score.

## Reproducible Commands
```bash
python3 models/train_baselines.py --samples 1200
python3 models/evaluate.py --metrics models/results/baseline_metrics.json
```
