# Post #3: Evaluating Machine Learning Models for Flaky Test Detection

## Hook
Model choice alone is not the decision. Threshold policy determines real CI behavior.

## Models Compared
- Logistic Regression
- Random Forest

## Why Simpler Models Still Matter
Linear models are easier to calibrate and explain for tabular CI signals, especially when data is limited.

## Key Trade-Off
- Higher precision: fewer unnecessary retries/quarantines
- Higher recall: fewer unstable tests slipping through

## Evidence in Repo
- Training script: `models/train_baselines.py`
- Evaluation CLI: `models/evaluate.py`
- Metrics artifact: `models/results/baseline_metrics.json`
- Supporting table: `docs/post-03-model-metrics.md`

## Reproducible Commands
```bash
python3 models/train_baselines.py --samples 1200
python3 models/evaluate.py --metrics models/results/baseline_metrics.json
```

## CTA
Do you optimize your flaky detector for precision first or recall first, and why?
