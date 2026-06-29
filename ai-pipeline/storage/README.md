# Media Storage Module

Module de stockage des médias (snapshots et clips vidéo) pour les alertes.

## Fonctionnalités

- **Capture de snapshots** : Sauvegarde d'images individuelles avec crop optionnel autour d'une bbox
- **Enregistrement de clips** : Buffer circulaire de N secondes pour enregistrer les clips vidéo
- **Nom automatique** : Fichiers nommés avec alert_id et timestamp
- **Stockage local** : Système de fichiers local
- **Nettoyage automatique** : Suppression des fichiers anciens

## Utilisation

```python
from ai_pipeline.storage import MediaStorage

# Initialisation
storage = MediaStorage(
    storage_dir="./data/media",
    clip_duration_seconds=10.0,
    fps=30.0
)

# Ajouter des frames au buffer (pour clips)
storage.add_frame(frame)

# Capturer un snapshot pour une alerte
snapshot_path = storage.capture_snapshot(frame, alert_id="alert-123", bbox=[x1, y1, x2, y2])

# Sauvegarder le clip
clip_path = storage.save_clip(alert_id="alert-123")

# Capturer les deux en une fois
snapshot_path, clip_path = storage.capture_alert_media(frame, alert_id="alert-123", bbox=[x1, y1, x2, y2])

# Nettoyer les anciens fichiers
storage.cleanup_old_media(max_age_hours=24)

# Statistiques de stockage
stats = storage.get_storage_stats()
```

## Structure des répertoires

```
data/media/
├── snapshots/
│   ├── snapshot_alert-123_20240629_143025.jpg
│   └── ...
└── clips/
    ├── clip_alert-123_20240629_143025.mp4
    └── ...
```

## Configuration

- `storage_dir` : Répertoire racine du stockage (défaut: `./data/media`)
- `snapshot_dir` : Sous-répertoire pour les snapshots (défaut: `snapshots`)
- `clip_dir` : Sous-répertoire pour les clips (défaut: `clips`)
- `clip_duration_seconds` : Durée du buffer clip en secondes (défaut: 10.0)
- `fps` : Frames par seconde pour l'enregistrement (défaut: 30.0)

## Intégration avec le pipeline IA

Le module est intégré dans `ai-pipeline/inference/detector.py` pour capturer automatiquement les médias lors des alertes.
