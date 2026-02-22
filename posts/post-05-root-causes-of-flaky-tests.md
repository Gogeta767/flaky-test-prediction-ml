# Post #5: The Engineering Causes Behind Flaky Tests in Modern Systems

## Hook
Prediction can route attention, but only root-cause fixes reduce long-term flakiness.

## Core Root-Cause Classes
- Async timing/race conditions
- Shared mutable state
- Network/dependency instability
- Microservice startup and environment drift
- Brittle test design

## Practical Framework
For each flaky signature, map:
- observable signals
- likely cause class
- explicit remediation pattern

## Evidence in Repo
- Taxonomy: `docs/root-causes-taxonomy.md`
- Supporting matrix: `docs/post-05-root-cause-matrix.md`

## Example Mapping
Signal: rising `duration_var_ms` + retry spikes  
Cause class: race condition/timing instability  
Fix: event-driven waits + deterministic synchronization points

## CTA
Which root-cause class is currently the biggest source of flaky failures in your org?
