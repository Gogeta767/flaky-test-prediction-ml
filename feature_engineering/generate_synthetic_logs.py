import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TestProfile:
    name: str
    flaky_prob: float
    base_duration_ms: int
    retry_lambda: float


def build_profiles() -> list[TestProfile]:
    return [
        TestProfile("auth.spec::login_success", flaky_prob=0.03, base_duration_ms=210, retry_lambda=0.05),
        TestProfile("checkout.spec::payment_flow", flaky_prob=0.32, base_duration_ms=850, retry_lambda=0.40),
        TestProfile("orders.spec::list_recent", flaky_prob=0.08, base_duration_ms=370, retry_lambda=0.10),
        TestProfile("profile.spec::upload_avatar", flaky_prob=0.27, base_duration_ms=620, retry_lambda=0.35),
        TestProfile("search.spec::filter_results", flaky_prob=0.05, base_duration_ms=300, retry_lambda=0.08),
        TestProfile("notifications.spec::websocket_push", flaky_prob=0.38, base_duration_ms=710, retry_lambda=0.50),
    ]


def generate_runs(total_runs: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    profiles = build_profiles()

    rows = []
    start_ts = pd.Timestamp("2026-01-01T09:00:00Z")
    browsers = ["chromium", "firefox", "webkit"]

    for run in range(total_runs):
        run_id = f"run-{run + 1:04d}"
        timestamp = start_ts + pd.Timedelta(minutes=run * 7)

        for profile in profiles:
            browser = browsers[run % len(browsers)]
            headless = bool(run % 2 == 0)

            failed = rng.random() < profile.flaky_prob
            retry_count = int(rng.poisson(profile.retry_lambda)) if failed else 0

            duration_noise = rng.normal(loc=0.0, scale=70.0 + profile.flaky_prob * 150.0)
            duration_ms = max(80, int(profile.base_duration_ms + duration_noise + retry_count * 45))

            network_latency = max(5.0, float(rng.normal(35.0 + 45.0 * profile.flaky_prob, 12.0)))
            cpu_load = min(100.0, max(2.0, float(rng.normal(43.0 + 20.0 * profile.flaky_prob, 10.0))))
            memory_usage = max(100.0, float(rng.normal(470.0 + profile.base_duration_ms * 0.45, 55.0)))

            rows.append(
                {
                    "test_name": profile.name,
                    "run_id": run_id,
                    "duration_ms": duration_ms,
                    "pass_fail": 0 if failed else 1,
                    "retry_count": retry_count,
                    "browser": browser,
                    "headless_mode": headless,
                    "timestamp": timestamp.isoformat(),
                    "cpu_load": round(cpu_load, 2),
                    "memory_usage": round(memory_usage, 2),
                    "network_latency": round(network_latency, 2),
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic CI run logs for flaky test research.")
    parser.add_argument(
        "--output",
        default="data/processed/synthetic_ci_runs.csv",
        help="Output CSV path for run-level synthetic logs.",
    )
    parser.add_argument("--runs", type=int, default=80, help="Number of CI runs to simulate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    df = generate_runs(total_runs=args.runs, seed=args.seed)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Wrote synthetic run-level dataset: {output_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
