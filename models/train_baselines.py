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
            "label_flaky": label_flaky,
        }
    )


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
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples", type=int, default=1200)
    args = parser.parse_args()

    df = build_modeling_dataset(seed=args.seed, n_samples=args.samples)

    X = df[FEATURE_COLUMNS]
    y = df["label_flaky"]

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
    for model_name, model_result in results["models"].items():
        p50 = next(m for m in model_result["threshold_metrics"] if m["threshold"] == 0.50)
        print(
            f"{model_name}: ROC-AUC={model_result['roc_auc']:.3f}, "
            f"precision@0.5={p50['precision']:.3f}, recall@0.5={p50['recall']:.3f}"
        )


if __name__ == "__main__":
    main()
