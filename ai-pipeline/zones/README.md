# Module de Gestion des Zones

Ce module gère les zones d'intrusion et la détection de regroupement de personnes.

## Fonctionnalités

### ZoneManager
- **CRUD de zones** : Création, lecture, mise à jour, suppression de zones géométriques
- **Types de zones** : INTRUSION, CROWD, SAFE
- **Stockage JSON** : Persistance des zones dans un fichier JSON
- **Calculs géométriques** : Utilise Shapely pour les tests d'appartenance point/polygone

### CrowdDetector
- **Comptage de personnes** : Compte les personnes distinctes dans une zone
- **Fenêtre temporelle** : Vérifie le seuil sur une période donnée
- **Anti faux positifs** : Exige une durée minimum pour confirmer un regroupement

## Utilisation

```python
from zones import ZoneManager, ZoneType, CrowdDetector

# Initialiser le gestionnaire de zones
zone_manager = ZoneManager(storage_path="zones.json")

# Créer une zone d'intrusion
zone = zone_manager.create_zone(
    zone_id="perimetre-nord",
    name="Périmètre Nord",
    zone_type=ZoneType.INTRUSION,
    polygon=[(100, 100), (400, 100), (400, 400), (100, 400)]
)

# Vérifier une intrusion
is_intrusion = zone_manager.check_intrusion(bbox=[150, 150, 250, 250], zone_id="perimetre-nord")

# Initialiser le détecteur de regroupement
crowd_detector = CrowdDetector(min_person_threshold=5, min_duration=10.0)

# Mettre à jour avec les tracks actuels
crowd_events = crowd_detector.update(tracks, zone_manager)
```

## Structure

- `zone_manager.py` : Gestion des zones géométriques
- `crowd_detector.py` : Détection de regroupement
- `requirements.txt` : Dépendances (shapely)

## Dépendances

- **shapely** (BSD) : Calculs géométriques
