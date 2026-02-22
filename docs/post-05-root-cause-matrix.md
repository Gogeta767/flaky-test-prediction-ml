# Post #5 Root Cause Matrix

| Cause Class | Typical Signal | First Mitigation |
|---|---|---|
| Async timing/races | retry spikes + timeout variance | event-based waits |
| Shared state leakage | order-dependent failures | strict setup/teardown reset |
| Network instability | p95 latency spikes + transient 5xx | dependency test doubles + bounded retry |
| Startup/env drift | early-stage pipeline failures | readiness gates + pinned env |
| Brittle tests | fails on minor refactors | semantic selectors + stable assertions |
