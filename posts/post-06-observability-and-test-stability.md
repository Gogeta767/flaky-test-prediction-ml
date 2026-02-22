# Post #6: Observability Signals That Reveal Test Instability

## Hook
Flaky behavior becomes actionable when logs, metrics, and timing signals are combined into a ranked stability view.

## Signal Stack
- Logs: retry/error signatures
- Metrics: fail rate, duration spread, retry rate
- Timing context: latency and execution variance

## Instability Ranking
Compute an `instability_score` and use it to prioritize tests for remediation instead of reacting to failures one by one.

## Evidence in Repo
- Notebook: `notebooks/observability_signals.ipynb`
- Supporting table: `docs/post-06-observability-ranking.md`

## Practical Loop
Extract signals -> rank unstable tests -> map to root cause -> fix -> measure post-fix stability.

## CTA
If you had to track only 3 observability signals for flaky tests, which ones would you choose?
