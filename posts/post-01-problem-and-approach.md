# Post #1: Why Flaky Tests Need ML in CI/CD

## Hook
Flaky tests are expensive because they look like product failures even when code is fine. Teams lose time in reruns and triage instead of shipping.

## Problem Statement
A flaky test fails non-deterministically without meaningful code change. This creates false alarms, release friction, and low trust in CI signals.

## Approach
Use historical test execution behavior to estimate `p_flaky` per test and prioritize mitigation before instability spreads.

## Experimental Framing
- Repeated runs under controlled conditions
- Feature extraction from run-level logs
- Binary flakiness labels from pass/fail variability
- Model comparison + CI threshold simulation

## Evidence in Repo
- Roadmap and artifacts: `README.md`
- Baseline notebook: `notebooks/flaky_test_prediction_baseline.ipynb`

## CTA
How does your team currently separate real regressions from flaky noise in CI?
