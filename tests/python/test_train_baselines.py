from pathlib import Path

import pandas as pd

from models.train_baselines import LABEL_COLUMN, load_modeling_data


def test_load_modeling_data_prefers_real_features_and_augments(tmp_path: Path) -> None:
    dataset = pd.DataFrame(
        {
            "fail_rate": [0.1, 0.5, 0.2, 0.7],
            "retry_rate": [0.0, 0.3, 0.1, 0.4],
            "duration_var_ms": [1000.0, 12000.0, 2500.0, 15000.0],
            "duration_cv": [0.08, 0.33, 0.15, 0.38],
            "max_fail_streak": [0, 3, 1, 4],
            "network_latency_mean": [25.0, 65.0, 35.0, 80.0],
            "cpu_load_mean": [35.0, 70.0, 45.0, 85.0],
            LABEL_COLUMN: [0, 1, 0, 1],
        }
    )
    path = tmp_path / "features.csv"
    dataset.to_csv(path, index=False)

    loaded, source = load_modeling_data(path, seed=42, target_rows=40, use_synthetic=False)

    assert source == "real_features_augmented"
    assert len(loaded) == 40
    assert loaded[LABEL_COLUMN].nunique() == 2
