# Post #1: Why Flaky Tests Need ML in CI/CD

## Problem Statement
Flaky tests fail non-deterministically without code changes, slowing CI/CD and eroding trust in automation.

## High-Level ML Approach
Model flaky behavior from historical execution signals (failure rate, retries, duration variance) and predict flakiness probability per test.

## Experimental Framing
Use repeated controlled runs in a stable code baseline, construct labels from pass/fail variability, and compare baseline models with CI policy simulation.
