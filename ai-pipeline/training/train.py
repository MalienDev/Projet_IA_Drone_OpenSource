"""
Training script for weapon detection model using Ultralytics YOLO.
"""

import os
from pathlib import Path
from ultralytics import YOLO


def train_weapon_model(
    data_yaml: str,
    model_size: str = "n",
    epochs: int = 100,
    batch_size: int = 16,
    imgsz: int = 640,
    device: str = "auto",
    project: str = "runs/train",
    name: str = "weapon_detection",
    exist_ok: bool = True,
    patience: int = 20,
    **kwargs
):
    """
    Train a YOLO model for weapon detection.

    Args:
        data_yaml: Path to data.yaml file
        model_size: Model size (n, s, m, l, x) - default 'n' for nano (fastest)
        epochs: Number of training epochs
        batch_size: Batch size for training
        imgsz: Image size for training
        device: Device to use (auto, cpu, 0, 1, etc.)
        project: Project directory for saving results
        name: Experiment name
        exist_ok: Whether to overwrite existing experiment
        patience: Early stopping patience
        **kwargs: Additional arguments to pass to YOLO.train()

    Returns:
        Trained model path
    """
    # Load pretrained YOLO model
    model = YOLO(f"yolov8{model_size}.pt")

    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        project=project,
        name=name,
        exist_ok=exist_ok,
        patience=patience,
        **kwargs
    )

    # Get the path to the best model
    best_model_path = Path(project) / name / "weights" / "best.pt"

    print(f"Training completed. Best model saved at: {best_model_path}")
    return str(best_model_path)


if __name__ == "__main__":
    # Default training configuration
    # Get project root (2 levels up from training/)
    project_root = Path(__file__).parent.parent.parent
    data_yaml = str(project_root / "datasets" / "dataset_merged" / "data.yaml")
    
    # Check if data.yaml exists
    if not os.path.exists(data_yaml):
        print(f"Error: data.yaml not found at {data_yaml}")
        print("Please ensure the dataset is correctly placed.")
        exit(1)

    # Train the model
    best_model = train_weapon_model(
        data_yaml=data_yaml,
        model_size="n",  # Use nano model for faster training
        epochs=100,
        batch_size=16,
        imgsz=640,
        device="auto",  # Will use GPU if available, else CPU
        patience=20
    )
