import argparse
import json
from pathlib import Path


def format_threshold_row(row: dict) -> str:
    return (
        f"t={row['threshold']:.2f} | "
        f"acc={row['accuracy']:.3f} "
        f"prec={row['precision']:.3f} "
        f"rec={row['recall']:.3f} "
        f"f1={row['f1']:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print baseline model evaluation summary.")
    parser.add_argument("--metrics", default="models/results/baseline_metrics.json", help="Metrics JSON path.")
    args = parser.parse_args()

    metrics_path = Path(args.metrics)
    metrics = json.loads(metrics_path.read_text())

    print("Dataset")
    print(f"  rows={metrics['dataset']['rows']} positive_rate={metrics['dataset']['positive_rate']:.3f}")

    print("\nModel Comparison")
    for model_name, model_metrics in metrics["models"].items():
        print(f"\n- {model_name}")
        print(f"  roc_auc={model_metrics['roc_auc']:.3f}")
        for row in model_metrics["threshold_metrics"]:
            print(f"  {format_threshold_row(row)}")


if __name__ == "__main__":
    main()
