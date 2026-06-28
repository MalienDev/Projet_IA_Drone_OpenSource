"""
Evaluation script for weapon detection model.
"""

import os
from pathlib import Path
from ultralytics import YOLO
import json


def evaluate_weapon_model(
    model_path: str,
    data_yaml: str,
    device: str = "auto",
    project: str = "runs/evaluate",
    name: str = "weapon_detection_eval",
    **kwargs
):
    """
    Evaluate a trained YOLO model for weapon detection.

    Args:
        model_path: Path to the trained model weights (.pt)
        data_yaml: Path to data.yaml file
        device: Device to use (auto, cpu, 0, 1, etc.)
        project: Project directory for saving results
        name: Evaluation name
        **kwargs: Additional arguments to pass to YOLO.val()

    Returns:
        Dictionary with evaluation metrics
    """
    # Load the trained model
    model = YOLO(model_path)

    # Validate the model
    results = model.val(
        data=data_yaml,
        device=device,
        project=project,
        name=name,
        **kwargs
    )

    # Extract metrics
    metrics = {
        "mAP50": results.box.map50,
        "mAP50-95": results.box.map,
        "precision": results.box.mp,
        "recall": results.box.mr,
        "f1": 2 * (results.box.mp * results.box.mr) / (results.box.mp + results.box.mr) if (results.box.mp + results.box.mr) > 0 else 0,
    }

    print("Evaluation Results:")
    print(f"  mAP50: {metrics['mAP50']:.4f}")
    print(f"  mAP50-95: {metrics['mAP50-95']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall: {metrics['recall']:.4f}")
    print(f"  F1 Score: {metrics['f1']:.4f}")

    return metrics


if __name__ == "__main__":
    # Default evaluation configuration
    model_path = "runs/train/weapon_detection/weights/best.pt"
    data_yaml = "datasets/dataset_merged/data.yaml"

    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        print("Please train the model first using train.py")
        exit(1)

    # Check if data.yaml exists
    if not os.path.exists(data_yaml):
        print(f"Error: data.yaml not found at {data_yaml}")
        exit(1)

    # Evaluate the model
    metrics = evaluate_weapon_model(
        model_path=model_path,
        data_yaml=data_yaml,
        device="auto"
    )

    # Save metrics to JSON
    metrics_path = Path("runs/evaluate/weapon_detection_eval/metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nMetrics saved to: {metrics_path}")
