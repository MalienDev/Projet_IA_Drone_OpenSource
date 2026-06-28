# Weapon Detection Model - Performance Report

## Training Configuration

**Date**: 2026-06-28
**Model**: YOLOv8n (nano)
**Dataset**: Weapon_Detection_for_Yolo (Kaggle)

### Dataset Statistics
- **Full dataset**:
  - Train: 18,186 images
  - Val: 4,546 images
  - Test: 623 images
  - Classes: 1 (Weapon)

- **Training subset** (CPU test):
  - Train: 500 images
  - Val: 100 images
  - Classes: 1 (Weapon)

### Training Parameters (CPU Test)
- **Epochs**: 1 (technical test only)
- **Batch size**: 8
- **Image size**: 640x640
- **Device**: CPU (Intel Core i5-10210U 1.60GHz)
- **Training time**: ~14 minutes
- **Optimizer**: AdamW

## Evaluation Results (CPU Test - 1 Epoch, Subset)

| Metric | Value |
|--------|-------|
| **mAP50** | 0.0625 (6.25%) |
| **mAP50-95** | 0.0213 (2.13%) |
| **Precision** | 0.0248 (2.48%) |
| **Recall** | 0.5097 (50.97%) |
| **F1 Score** | 0.0473 (4.73%) |

### Inference Speed
- **Preprocess**: 2.2ms per image
- **Inference**: 229.4ms per image
- **Postprocess**: 16.1ms per image
- **Total**: ~247ms per image (~4 FPS on CPU)

## Analysis & Limitations

### 1. Low Performance Expected
The metrics above are **very low** but **expected** for this configuration:
- **1 epoch only**: The model barely started learning (typically 50-100+ epochs needed)
- **Subset dataset**: Only 500 training images vs 18,186 in full dataset
- **CPU training**: Limited computational resources

### 2. Domain Gap (Critical)
**Important limitation**: The dataset is composed of **ground-level images** (standard cameras), not aerial/drone views. This creates a significant domain gap:
- **Angle**: Ground-level vs aerial (top-down) perspective
- **Scale**: Weapons appear larger/close in ground images vs small/distant in aerial views
- **Resolution**: Typical camera resolution vs drone camera at altitude
- **Context**: Different backgrounds, lighting conditions

**Impact**: The model trained on this dataset will likely perform poorly on real drone footage without:
- Fine-tuning on aerial/drone images
- Data augmentation simulating aerial views
- Or a dedicated aerial weapon dataset

### 3. Weapon Detection from Altitude
From a typical drone altitude (50-150m), a weapon represents only a few pixels in the image. This makes detection extremely challenging:
- **Small object detection**: Requires SAHI (Slicing Aided Hyper Inference) or similar techniques
- **Zoom confirmation**: If gimbal allows, optical zoom for second-pass detection before alerting
- **High false positive rate**: Small objects are easily confused with other objects

## Recommendations for Production

### 1. Training Improvements
- **GPU training**: Use NVIDIA GPU with CUDA for 100+ epochs
- **Full dataset**: Train on all 18,186 images
- **Data augmentation**: Add aerial-view augmentations (rotation, scale, perspective)
- **SAHI integration**: Enable SAHI for small object detection (requires GPU)
- **Transfer learning**: Consider fine-tuning on aerial/drone images if available

### 2. Model Selection
- **Model size**: Consider YOLOv8s or YOLOv8m for better accuracy (requires more GPU memory)
- **Custom architecture**: Explore models optimized for small object detection

### 3. Operational Constraints
- **Confirmation required**: All weapon detections MUST be flagged as "to confirm by operator"
- **High confidence threshold**: Use 0.8+ confidence to reduce false positives
- **Zoom confirmation**: Implement optical zoom for second-pass detection if gimbal supports it
- **Multi-frame consensus**: Require detection over N consecutive frames before alerting

### 4. Dataset Strategy
- **Aerial dataset**: Source or create a dataset with aerial/drone views of weapons
- **Synthetic data**: Consider synthetic data generation for aerial weapon scenarios
- **Domain adaptation**: Implement domain adaptation techniques to bridge ground-to-aerial gap

## Current Model Status

**File**: `ai-pipeline/models/weapon_detection.pt`
**Status**: Technical test model only - NOT production ready
**Use case**: Pipeline validation and integration testing

## Next Steps

1. **Integration**: Integrate the model into the detection pipeline with high confidence threshold
2. **Testing**: Test on real aerial footage (Phase 9) to validate domain gap impact
3. **Retraining**: Plan for GPU-based training with full dataset and aerial augmentations
4. **Monitoring**: Track false positive/negative rates in production

## Conclusion

The current model serves as a **technical proof-of-concept** demonstrating the training pipeline works. However, it is **not suitable for production use** due to:
- Insufficient training (1 epoch)
- Domain gap (ground-level vs aerial)
- Small object detection challenges from drone altitude

A production-ready model requires:
- GPU-based training (100+ epochs)
- Full dataset (18,186+ images)
- Aerial/drone-specific data
- SAHI for small object detection
- Extensive validation on real drone footage

**License Note**: YOLO models are AGPL-3.0 licensed. Acceptable for internal use, but consider implications if deploying externally.
