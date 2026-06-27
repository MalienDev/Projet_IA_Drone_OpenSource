# Module de Tracking Multi-Objets

Ce module gère le suivi des objets détectés entre les frames vidéo.

## Fonctionnalités

- **ByteTrack intégré** : Utilise l'intégration native d'Ultralytics YOLOv8
- **Track ID stables** : Maintient des identifiants cohérents pour chaque objet
- **Historique des positions** : Conserve les 100 dernières positions de chaque objet
- **Calcul de vélocité** : Permet de calculer la vitesse de déplacement
- **Nettoyage automatique** : Supprime les tracks non vus depuis > 30 frames

## Utilisation

```python
from tracking import MultiObjectTracker

# Initialiser le tracker
tracker = MultiObjectTracker(tracker_type="bytetrack")

# Mettre à jour avec les résultats YOLO (avec tracking activé)
tracked_objects = tracker.update(results)

# Accéder aux tracks
all_tracks = tracker.get_all_tracks()
person_tracks = tracker.get_tracks_by_class("person")

# Réinitialiser
tracker.reset()
```

## Structure

- `tracker.py` : Implémentation principale du tracker
- `requirements.txt` : Dépendances (déjà incluses dans inference)

## Intégration

Le tracker est utilisé dans le pipeline de détection principal (`ai-pipeline/inference/detector.py`) en activant le tracking YOLO :
```python
results = model.track(frame, persist=True, ...)
```
