import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "test_name",
    "run_id",
    "duration_ms",
    "pass_fail",
    "retry_count",
    "browser",
    "headless_mode",
    "timestamp",
}


def to_numeric_pass_fail(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(int)

    normalized = series.astype(str).str.strip().str.lower()
    true_values = {"1", "true", "pass", "passed", "success"}
    false_values = {"0", "false", "fail", "failed", "error"}

    mapped = normalized.map(lambda v: 1 if v in true_values else (0 if v in false_values else None))
    if mapped.isna().any():
        raise ValueError("pass_fail contains values that cannot be mapped to binary pass/fail.")
    return mapped.astype(int)


def max_fail_streak(values: pd.Series) -> int:
    streak = 0
    best = 0
    for v in values.astype(int):
        if v == 0:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return best


def build_feature_table(run_df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(run_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = run_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    if df["timestamp"].isna().any():
        raise ValueError("timestamp column has invalid datetime values.")

    df["pass_fail"] = to_numeric_pass_fail(df["pass_fail"])
    df = df.sort_values(["test_name", "timestamp"]).reset_index(drop=True)

    grouped = df.groupby("test_name", as_index=False)

    features = grouped.agg(
        total_runs=("run_id", "count"),
        pass_rate=("pass_fail", "mean"),
        retry_rate=("retry_count", "mean"),
        duration_mean_ms=("duration_ms", "mean"),
        duration_std_ms=("duration_ms", "std"),
        duration_var_ms=("duration_ms", "var"),
        p95_duration_ms=("duration_ms", lambda s: float(s.quantile(0.95))),
        browser_count=("browser", "nunique"),
        headless_share=("headless_mode", "mean"),
    )

    if "network_latency" in df.columns:
        lat_stats = grouped["network_latency"].mean().rename(columns={"network_latency": "network_latency_mean"})
        features = features.merge(lat_stats, on="test_name", how="left")

    if "cpu_load" in df.columns:
        cpu_stats = grouped["cpu_load"].mean().rename(columns={"cpu_load": "cpu_load_mean"})
        features = features.merge(cpu_stats, on="test_name", how="left")

    if "memory_usage" in df.columns:
        mem_stats = grouped["memory_usage"].mean().rename(columns={"memory_usage": "memory_usage_mean"})
        features = features.merge(mem_stats, on="test_name", how="left")

    features["fail_rate"] = 1.0 - features["pass_rate"]
    features["duration_cv"] = features["duration_std_ms"] / features["duration_mean_ms"]

    streaks = (
        df.groupby("test_name")["pass_fail"]
        .apply(max_fail_streak)
        .rename("max_fail_streak")
        .reset_index()
    )
    features = features.merge(streaks, on="test_name", how="left")

    # Label as flaky when outcomes vary across runs in unchanged code context.
    features["label_flaky"] = ((features["pass_rate"] > 0.0) & (features["pass_rate"] < 1.0)).astype(int)

    numeric_cols = [
        "pass_rate",
        "fail_rate",
        "retry_rate",
        "duration_mean_ms",
        "duration_std_ms",
        "duration_var_ms",
        "p95_duration_ms",
        "headless_share",
        "duration_cv",
    ]
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].fillna(0.0)

    optional_numeric = ["network_latency_mean", "cpu_load_mean", "memory_usage_mean"]
    for col in optional_numeric:
        if col in features.columns:
            features[col] = features[col].fillna(0.0)

    return features.sort_values("fail_rate", ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build per-test feature table for flaky test prediction.")
    parser.add_argument(
        "--input",
        default="data/processed/synthetic_ci_runs.csv",
        help="Input CSV path with run-level CI test logs.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/sample_features.csv",
        help="Output CSV path for per-test feature table.",
    )
    args = parser.parse_args()

    run_df = pd.read_csv(args.input)
    feature_df = build_feature_table(run_df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(output_path, index=False)

    print(f"Wrote feature table: {output_path} ({len(feature_df)} rows)")
    print(feature_df[["test_name", "fail_rate", "retry_rate", "duration_var_ms", "label_flaky"]].head())


if __name__ == "__main__":
    main()
