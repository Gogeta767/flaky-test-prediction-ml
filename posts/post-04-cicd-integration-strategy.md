# Post #4: Integrating Flaky Test Prediction into CI Pipelines

## Where Prediction Runs
- Post-test scoring from latest execution logs (recommended first)
- Optional pre-test risk scoring for selective retries

## Probability Thresholding
Use a configurable threshold `p_flaky >= t` to decide mitigation actions.

## Risk-Based Gating
- High risk: retry/quarantine with alerts
- Medium risk: allow run but flag
- Low risk: normal policy

## Do Not Block Pipelines by Default
Start with soft actions and observability before hard blocking.
