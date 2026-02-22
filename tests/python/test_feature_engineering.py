import pandas as pd

from feature_engineering.build_features import build_feature_table, to_numeric_pass_fail


def test_to_numeric_pass_fail_handles_strings_and_bool_values() -> None:
    raw = pd.Series(["pass", "failed", "TRUE", "0", True, False])
    numeric = to_numeric_pass_fail(raw)
    assert numeric.tolist() == [1, 0, 1, 0, 1, 0]


def test_build_feature_table_creates_flaky_labels() -> None:
    run_df = pd.DataFrame(
        [
            {
                "test_name": "stable.spec::always_pass",
                "run_id": "r1",
                "duration_ms": 200,
                "pass_fail": 1,
                "retry_count": 0,
                "browser": "chromium",
                "headless_mode": True,
                "timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "test_name": "stable.spec::always_pass",
                "run_id": "r2",
                "duration_ms": 210,
                "pass_fail": 1,
                "retry_count": 0,
                "browser": "chromium",
                "headless_mode": True,
                "timestamp": "2026-01-01T00:10:00Z",
            },
            {
                "test_name": "flaky.spec::sometimes_fail",
                "run_id": "r1",
                "duration_ms": 500,
                "pass_fail": 0,
                "retry_count": 1,
                "browser": "firefox",
                "headless_mode": False,
                "timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "test_name": "flaky.spec::sometimes_fail",
                "run_id": "r2",
                "duration_ms": 410,
                "pass_fail": 1,
                "retry_count": 0,
                "browser": "firefox",
                "headless_mode": False,
                "timestamp": "2026-01-01T00:10:00Z",
            },
        ]
    )

    features = build_feature_table(run_df)

    stable_row = features.loc[features["test_name"] == "stable.spec::always_pass"].iloc[0]
    flaky_row = features.loc[features["test_name"] == "flaky.spec::sometimes_fail"].iloc[0]

    assert stable_row["label_flaky"] == 0
    assert flaky_row["label_flaky"] == 1
    assert stable_row["fail_rate"] == 0.0
    assert flaky_row["fail_rate"] == 0.5
