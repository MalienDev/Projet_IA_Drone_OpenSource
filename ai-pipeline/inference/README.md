# Module Inference - Détection d'Objets

Module de détection d'objets en temps réel pour le pipeline de surveillance par drone.

## Fonctionnalités

- **Détection YOLO** : Utilise Ultralytics YOLOv8 pour détecter personnes et véhicules
- **SAHI** : Intégration de Slicing Aided Hyper Inference pour améliorer la détection des petits objets vus d'altitude
- **Consommation de flux** : Compatible avec les flux MediaMTX (RTSP/RTMP/SRT)
- **Affichage temps réel** : Fenêtre OpenCV avec bounding boxes colorées et FPS
- **Configuration flexible** : Seuils de confiance, classes cibles, device d'inférence

## Installation

```bash
cd ai-pipeline/inference
pip install -r requirements.txt
```

## Configuration

La configuration se fait via la classe `DetectionConfig` dans `config.py` :

```python
from inference.config import DetectionConfig

config = DetectionConfig(
    model_name="yolov8n.pt",  # Modèle YOLO (n, s, m, l, x)
    confidence_threshold=0.5,  # Seuil de confiance
    use_sahi=True,  # Activer SAHI pour petits objets
    device="cpu",  # cpu, cuda, mps
    rtsp_url="rtsp://localhost:8554/drone-01-los"
)
```

### Variables d'environnement

- `INFERENCE_MODEL` : Nom du modèle YOLO
- `INFERENCE_DEVICE` : Device d'inférence (cpu/cuda)
- `INFERENCE_RTSP_URL` : URL du flux RTSP
- `INFERENCE_CONFIDENCE` : Seuil de confiance

## Classes détectées

Par défaut, le module détecte les classes COCO suivantes :
- `person` : Personnes
- `bicycle` : Vélos
- `car` : Voitures
- `motorcycle` : Motos
- `truck` : Camions
- `bus` : Bus

## Utilisation

### Ligne de commande

```bash
python -m inference.detector
```

### Depuis un script Python

```python
from inference import ObjectDetector, default_config

# Créer le détecteur avec la config par défaut
detector = ObjectDetector(default_config)

# Traiter le flux en continu avec affichage
detector.process_stream(display=True)
```

### Traitement d'une frame unique

```python
import cv2
from inference import ObjectDetector, default_config

detector = ObjectDetector(default_config)

# Lire une frame
frame = cv2.imread("image.jpg")

# Détecter les objets
detections = detector.detect_frame(frame)

# Dessiner les bounding boxes
frame_with_boxes = detector.draw_detections(frame, detections)

cv2.imshow("Detection", frame_with_boxes)
cv2.waitKey(0)
```

## Structure du module

```
inference/
├── __init__.py          # Exports publics
├── config.py            # Configuration
├── detector.py          # Détecteur principal
├── requirements.txt     # Dépendances
├── README.md           # Documentation
└── tests/
    ├── __init__.py
    └── test_detector.py # Tests unitaires
```

## Tests

```bash
cd ai-pipeline/inference
pytest tests/ -v
```

## Performance

Sur un CPU standard avec YOLOv8n :
- **Sans SAHI** : ~15-20 FPS (640x640)
- **Avec SAHI** : ~5-10 FPS (dépend de la slice size)

Sur GPU NVIDIA avec YOLOv8n :
- **Sans SAHI** : ~100+ FPS
- **Avec SAHI** : ~30-50 FPS

## Licence

- Code du projet : MIT
- Ultralytics YOLO : AGPL-3.0
- SAHI : MIT
- OpenCV : Apache-2.0

## Notes

- Le modèle YOLOv8n est recommandé pour le CPU (rapide mais moins précis)
- SAHI est activé par défaut pour améliorer la détection des petits objets vus d'altitude drone
- Pour une production sur GPU, utiliser YOLOv8s ou YOLOv8m pour un meilleur compromis performance/précision
