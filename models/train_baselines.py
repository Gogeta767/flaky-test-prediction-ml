import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "fail_rate",
    "retry_rate",
    "duration_var_ms",
    "duration_cv",
    "max_fail_streak",
    "network_latency_mean",
    "cpu_load_mean",
]
LABEL_COLUMN = "label_flaky"

CONTINUOUS_COLUMNS = [
    "fail_rate",
    "retry_rate",
    "duration_var_ms",
    "duration_cv",
    "network_latency_mean",
    "cpu_load_mean",
]


def build_modeling_dataset(seed: int, n_samples: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    fail_rate = rng.uniform(0.0, 0.75, n_samples)
    retry_rate = rng.uniform(0.0, 0.45, n_samples)
    duration_var_ms = rng.uniform(500, 18000, n_samples)
    duration_cv = rng.uniform(0.03, 0.40, n_samples)
    max_fail_streak = rng.integers(0, 6, n_samples)
    network_latency_mean = rng.uniform(15, 90, n_samples)
    cpu_load_mean = rng.uniform(20, 90, n_samples)

    linear_score = (
        2.7 * fail_rate
        + 1.9 * retry_rate
        + 1.1 * duration_cv
        + 0.18 * max_fail_streak
        + 0.012 * (network_latency_mean - 35)
        + 0.004 * (duration_var_ms / 100.0)
        - 2.2
    )
    prob = 1 / (1 + np.exp(-linear_score))
    label_flaky = (rng.uniform(0, 1, n_samples) < prob).astype(int)

    return pd.DataFrame(
        {
            "fail_rate": fail_rate,
            "retry_rate": retry_rate,
            "duration_var_ms": duration_var_ms,
            "duration_cv": duration_cv,
            "max_fail_streak": max_fail_streak,
            "network_latency_mean": network_latency_mean,
            "cpu_load_mean": cpu_load_mean,
            LABEL_COLUMN: label_flaky,
        }
    )


def normalize_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in FEATURE_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0

    if LABEL_COLUMN not in out.columns:
        raise ValueError(f"Missing required label column: {LABEL_COLUMN}")

    out[LABEL_COLUMN] = out[LABEL_COLUMN].astype(int)
    out["max_fail_streak"] = out["max_fail_streak"].astype(int)
    return out[FEATURE_COLUMNS + [LABEL_COLUMN]]


def augment_real_dataset(base_df: pd.DataFrame, seed: int, target_rows: int) -> pd.DataFrame:
    if len(base_df) >= target_rows:
        return base_df

    rng = np.random.default_rng(seed)
    class_0 = base_df[base_df[LABEL_COLUMN] == 0]
    class_1 = base_df[base_df[LABEL_COLUMN] == 1]
    if class_0.empty or class_1.empty:
        return base_df

    target_0 = target_rows // 2
    target_1 = target_rows - target_0
    sampled_0 = class_0.sample(n=target_0, replace=True, random_state=seed).reset_index(drop=True)
    sampled_1 = class_1.sample(n=target_1, replace=True, random_state=seed + 1).reset_index(drop=True)
    sampled = pd.concat([sampled_0, sampled_1], ignore_index=True)

    # Add light jitter to avoid exact duplicates while preserving class profile.
    for col in CONTINUOUS_COLUMNS:
        std = float(base_df[col].std()) if len(base_df) > 1 else 0.0
        noise_scale = max(std * 0.15, 0.02)
        sampled[col] = sampled[col] + rng.normal(0.0, noise_scale, size=len(sampled))

    sampled["fail_rate"] = sampled["fail_rate"].clip(lower=0.0, upper=1.0)
    sampled["retry_rate"] = sampled["retry_rate"].clip(lower=0.0, upper=1.0)
    sampled["duration_var_ms"] = sampled["duration_var_ms"].clip(lower=0.0)
    sampled["duration_cv"] = sampled["duration_cv"].clip(lower=0.0, upper=1.0)
    sampled["network_latency_mean"] = sampled["network_latency_mean"].clip(lower=0.0)
    sampled["cpu_load_mean"] = sampled["cpu_load_mean"].clip(lower=0.0, upper=100.0)

    sampled["max_fail_streak"] = sampled["max_fail_streak"].round().clip(lower=0).astype(int)
    sampled[LABEL_COLUMN] = sampled[LABEL_COLUMN].astype(int)

    # Prevent over-separable augmentation from producing misleadingly perfect metrics.
    flip_mask = rng.random(len(sampled)) < 0.06
    sampled.loc[flip_mask, LABEL_COLUMN] = 1 - sampled.loc[flip_mask, LABEL_COLUMN]

    return sampled


def load_modeling_data(
    dataset_path: Path,
    seed: int,
    target_rows: int,
    use_synthetic: bool,
) -> tuple[pd.DataFrame, str]:
    if not use_synthetic and dataset_path.exists():
        real_df = normalize_feature_columns(pd.read_csv(dataset_path))
        if real_df[LABEL_COLUMN].nunique() >= 2:
            augmented = augment_real_dataset(real_df, seed=seed, target_rows=target_rows)
            source = "real_features_augmented" if len(augmented) > len(real_df) else "real_features"
            return augmented, source

    return build_modeling_dataset(seed=seed, n_samples=target_rows), "synthetic"


def evaluate_threshold(y_true: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict:
    preds = (probabilities >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        preds,
        average="binary",
        zero_division=0,
    )
    return {
        "threshold": threshold,
        "accuracy": float(accuracy_score(y_true, preds)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline flaky-test classifiers.")
    parser.add_argument("--output", default="models/results/baseline_metrics.json", help="JSON output path.")
    parser.add_argument("--dataset", default="data/processed/sample_features.csv", help="Feature table CSV path.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples", type=int, default=1200)
    parser.add_argument("--use-synthetic", action="store_true", help="Force synthetic dataset mode.")
    args = parser.parse_args()

    df, dataset_source = load_modeling_data(
        dataset_path=Path(args.dataset),
        seed=args.seed,
        target_rows=args.samples,
        use_synthetic=args.use_synthetic,
    )

    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=args.seed,
        stratify=y,
    )

    models = {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=args.seed,
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            random_state=args.seed,
            class_weight="balanced",
            min_samples_leaf=3,
        ),
    }

    thresholds = [0.30, 0.50, 0.70]
    results: dict[str, dict] = {
        "dataset": {
            "source": dataset_source,
            "rows": int(len(df)),
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "positive_rate": float(y.mean()),
            "feature_columns": FEATURE_COLUMNS,
        },
        "models": {},
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        probabilities = model.predict_proba(X_test)[:, 1]
        model_result = {
            "roc_auc": float(roc_auc_score(y_test, probabilities)),
            "threshold_metrics": [evaluate_threshold(y_test.to_numpy(), probabilities, t) for t in thresholds],
        }

        if name == "logistic_regression":
            lr_model = model.named_steps["model"]
            model_result["coefficients"] = {
                feature: float(value)
                for feature, value in zip(FEATURE_COLUMNS, lr_model.coef_[0])
            }

        results["models"][name] = model_result

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))

    print(f"Wrote baseline metrics: {output_path}")
    print(f"Dataset source: {dataset_source}")
    for model_name, model_result in results["models"].items():
        p50 = next(m for m in model_result["threshold_metrics"] if m["threshold"] == 0.50)
        print(
            f"{model_name}: ROC-AUC={model_result['roc_auc']:.3f}, "
            f"precision@0.5={p50['precision']:.3f}, recall@0.5={p50['recall']:.3f}"
        )


if __name__ == "__main__":
    main()
