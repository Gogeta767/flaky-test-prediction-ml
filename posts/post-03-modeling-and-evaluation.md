# Post #3: Evaluating Machine Learning Models for Flaky Test Detection

## Models Compared
- Logistic Regression
- Random Forest

## Why Simple Models Can Win
For tabular CI features and limited data, linear models are often more stable and easier to calibrate.

## Precision vs Recall in CI
- Higher precision reduces unnecessary retries/quarantine.
- Higher recall catches more flaky tests but can increase false positives.

## CI Trade-off
Tune thresholds based on pipeline cost of false positives versus false negatives.
