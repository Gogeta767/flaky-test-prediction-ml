# Post #4: Integrating Flaky Test Prediction into CI Pipelines

## Hook
A good predictor can still hurt delivery if integrated with the wrong gating policy.

## Integration Pattern
Start with post-test scoring and soft actions before hard pipeline blocking.

## Threshold-Guided Actions
- High risk (`p_flaky >= t_high`): retry/quarantine + alert
- Medium risk: tag for triage, do not block merge by default
- Low risk: normal CI path

## Why Cost Modeling Matters
In many CI systems, false negatives cost more than false positives. Threshold tuning should reflect that business cost.

## Evidence in Repo
- Simulator: `ci_integration/policy_simulator.py`
- Scenarios: `ci_integration/threshold_scenarios.csv`
- Supporting table: `docs/post-04-threshold-analysis.md`

## Reproducible Command
```bash
python3 ci_integration/policy_simulator.py \
  --metrics models/results/baseline_metrics.json \
  --model logistic_regression \
  --output ci_integration/threshold_scenarios.csv
```

## CTA
Would your CI process accept soft-gating first, or do you need hard-gating from day one?
