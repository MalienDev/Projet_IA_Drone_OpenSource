# Weapon Detection Training Module

This module contains scripts to train and evaluate a YOLO model for weapon detection.

## Dataset

The dataset is located at `datasets/dataset_merged/` and contains:
- **Train**: 18,186 images
- **Val**: 4,546 images
- **Test**: 623 images
- **Classes**: 1 (Weapon)

**Note**: This dataset is likely composed of ground-level images (standard cameras), not aerial/drone views. A domain gap (angle, scale, resolution) is expected and should be validated in Phase 9 with real aerial images.

## Installation

```bash
cd ai-pipeline/training
pip install -r requirements.txt
```

## Training

### Basic Training

```bash
python train.py
```

This will:
- Use YOLOv8n (nano) model for faster training
- Train for 100 epochs
- Use batch size 16
- Use image size 640x640
- Auto-detect GPU if available

### Custom Training

```python
from train import train_weapon_model

best_model = train_weapon_model(
    data_yaml="datasets/dataset_merged/data.yaml",
    model_size="n",  # n, s, m, l, x
    epochs=100,
    batch_size=16,
    imgsz=640,
    device="auto",
    patience=20
)
```

### Training Parameters

- **model_size**: Model size (n=nano, s=small, m=medium, l=large, x=extra-large)
  - Nano is fastest but less accurate
  - Larger models are more accurate but slower and require more GPU memory
- **epochs**: Number of training epochs (default: 100)
- **batch_size**: Batch size (default: 16, reduce if OOM)
- **imgsz**: Image size (default: 640)
- **device**: Device to use (auto, cpu, 0, 1, etc.)
- **patience**: Early stopping patience (default: 20 epochs)

## Evaluation

### Basic Evaluation

```bash
python evaluate.py
```

This will evaluate the best model on the validation set and output:
- mAP50 (mean Average Precision at IoU=0.5)
- mAP50-95 (mean Average Precision across IoU thresholds)
- Precision
- Recall
- F1 Score

### Custom Evaluation

```python
from evaluate import evaluate_weapon_model

metrics = evaluate_weapon_model(
    model_path="runs/train/weapon_detection/weights/best.pt",
    data_yaml="datasets/dataset_merged/data.yaml",
    device="auto"
)
```

## Output

Training results are saved to `runs/train/weapon_detection/`:
- `weights/best.pt`: Best model weights (based on validation mAP)
- `weights/last.pt`: Last epoch weights
- `results.csv`: Training metrics per epoch
- `confusion_matrix.png`: Confusion matrix visualization
- `PR_curve.png`: Precision-Recall curve
- `F1_curve.png`: F1 score curve

Evaluation results are saved to `runs/evaluate/weapon_detection_eval/`:
- `metrics.json`: JSON file with evaluation metrics
- Visualizations (confusion matrix, PR curve, etc.)

## GPU Requirements

Training on CPU is possible but very slow. A GPU with CUDA support is strongly recommended:
- **Minimum**: NVIDIA GPU with 4GB VRAM (for YOLOv8n, batch_size=8)
- **Recommended**: NVIDIA GPU with 8GB+ VRAM (for YOLOv8n, batch_size=16+)

## License

- **YOLO**: AGPL-3.0 (acceptable for internal use)
- **Dataset**: Check the dataset license from Kaggle
