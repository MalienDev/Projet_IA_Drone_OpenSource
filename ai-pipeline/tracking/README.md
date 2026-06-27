# Module de Tracking Multi-Objets

Ce module gère le suivi des objets détectés entre les frames vidéo et la classification du mode de déplacement.

## Fonctionnalités

### Tracking
- **ByteTrack intégré** : Utilise l'intégration native d'Ultralytics YOLOv8
- **Track ID stables** : Maintient des identifiants cohérents pour chaque objet
- **Historique des positions** : Conserve les 100 dernières positions de chaque objet
- **Calcul de vélocité** : Permet de calculer la vitesse de déplacement
- **Nettoyage automatique** : Supprime les tracks non vus depuis > 30 frames

### Classification de mouvement
- **Association personne↔moto** : Détecte si une personne est sur une moto
- **Calcul de vitesse** : Estime la vitesse en pixels/frame
- **Classification** : Distingue piéton vs moto vs inconnu
- **Stabilité temporelle** : Nécessite plusieurs frames consécutives pour confirmer une association

## Utilisation

### Tracking

```python
from tracking import MultiObjectTracker

# Initialiser le tracker
tracker = MultiObjectTracker(tracker_type="bytetrack")

# Mettre à jour avec les résultats YOLO (avec tracking activé)
tracked_objects = tracker.update(results)

# Accéder aux tracks
all_tracks = tracker.get_all_tracks()
person_tracks = tracker.get_tracks_by_class("person")

# Calculer la vitesse moyenne d'un track
speed = track.get_average_speed(min_history=5)

# Réinitialiser
tracker.reset()
```

### Classification de mouvement

```python
from tracking.movement_classifier import MovementClassifier, MovementType

# Initialiser le classifieur
classifier = MovementClassifier(
    association_distance_threshold=100.0,  # pixels
    min_association_frames=5,
    walking_speed_threshold=2.0  # pixels/frame
)

# Classifier le mouvement des personnes
classifications = classifier.classify(person_tracks, motorcycle_tracks)

# Accéder aux résultats
for classification in classifications:
    print(f"Track {classification.track_id}: {classification.movement_type.value}")
    print(f"Vitesse: {classification.speed_pixels_per_frame} pixels/frame")
    if classification.associated_vehicle_id:
        print(f"Véhicule associé: {classification.associated_vehicle_id}")
```

## Structure

- `tracker.py` : Implémentation principale du tracker (MultiObjectTracker, TrackedObject)
- `movement_classifier.py` : Classification du mode de déplacement (MovementClassifier)
- `tests/test_tracker.py` : Tests unitaires du tracker
- `tests/test_movement_classifier.py` : Tests unitaires du classifieur de mouvement
- `requirements.txt` : Dépendances (déjà incluses dans inference)

## Intégration

Le tracker est utilisé dans le pipeline de détection principal (`ai-pipeline/inference/detector.py`) en activant le tracking YOLO :
```python
results = model.track(frame, persist=True, ...)
```

La classification de mouvement est automatiquement activée lorsque le tracking est activé dans la configuration :
```python
config = DetectionConfig(use_tracking=True)
detector = ObjectDetector(config)
```

## Limitations

- **Vitesse en pixels/frame** : Sans télémétrie GPS/altitude, la vitesse est calculée en pixels/frame et non en m/s
- **Association moto** : Nécessite que la moto soit détectée comme un objet séparé de la personne
- **Stabilité** : L'association personne↔moto nécessite plusieurs frames consécutives (configurable via `min_association_frames`)

