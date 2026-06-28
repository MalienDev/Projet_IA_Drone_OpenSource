# Progression du Projet - Système de Surveillance par Drone

## Phase 0 — Cadrage & environnement ✅

### Objectif
Lever toutes les inconnues avant de coder et préparer l'environnement du projet.

### Informations collectées
- **Modèles de drone** : HALE (ex: RQ-4 Global Hawk) et MALE (ex: Elbit Hermes 900 Starliner, MQ-9 Reaper)
- **Type de sortie vidéo** : HDMI, HD-SDI et IP
- **Matériel GCS** : CPU standard + GPU NVIDIA standard
- **Résolution/FPS** :
  - Thermique (HD IR) : 1280x1024 @ 60 FPS
  - Jour (HD Day TV) : 4096x2880 @ 60 FPS
- **Nombre de drones simultanés** : 10
- **Bande passante BLOS** : 2 à 45 Mbps
- **Latence BLOS** : 600 à 1000 ms

### Livrables créés
- ✅ `docs/architecture.md` — Architecture détaillée avec spécifications techniques
- ✅ `.env.example` — Variables d'environnement pour Docker Compose
- ✅ Structure du dépôt créée (docs/, ingestion/, ai-pipeline/, backend/, frontend/, infra/, datasets/)

### Décisions techniques prises
- **MediaMTX** choisi pour l'ingestion unifiée (licence MIT)
- **YOLOv8/v11** choisi pour la détection (AGPL-3.0, acceptable pour usage interne)
- **SAHI** intégré pour améliorer la détection des petits objets vus d'altitude
- **ByteTrack** choisi pour le tracking multi-objets (MIT)
- **FastAPI** pour le backend (MIT)
- **Redis** comme bus de messages (BSD-3)
- **PostgreSQL + PostGIS** pour la persistance (PostgreSQL License / GPL-2)
- **React + Vite + TypeScript** pour le dashboard (MIT)
- **Leaflet + tuiles OSM auto-hébergées** pour la cartographie 100% locale

### Reste à faire
- [ ] README.md (description du projet)
- [ ] Validation Phase 0 par l'utilisateur

---

## Phase 1 — Ingestion vidéo unifiée ✅

### Objectif
Déployer MediaMTX et créer un simulateur de flux pour développer sans drone réel.

### Tâches
- [x] Déployer MediaMTX en conteneur (docker-compose.yml créé)
- [x] Configurer les endpoints RTSP/RTMP/SRT (ingestion/mediamtx.yml créé)
- [x] Créer un simulateur FFmpeg avec vidéo de test (scripts dans ai-pipeline/simulator/)
- [x] Démarrer MediaMTX via Docker Compose
- [x] Installer FFmpeg (déjà installé sur le système)
- [x] Générer vidéo de test (data/test-video.mp4)
- [x] Démarrer simulateur LOS via RTMP (adapté depuis RTSP pour stabilité)
- [x] Démarrer simulateur BLOS via RTMP
- [x] Vérifier la réception des flux par MediaMTX

### Décisions techniques prises
- **RTMP au lieu de RTSP** : Le protocole RTSP posait des problèmes de timeout (session timeout après 10s). RTMP s'est avéré plus stable pour le streaming continu depuis le simulateur FFmpeg.
- **Configuration MediaMTX** : Utilisation du mode `publisher` pour accepter les flux entrants et les republier.
- **Volume Docker** : Montage de `./data:/data` pour permettre à MediaMTX d'accéder aux fichiers locaux si nécessaire.
- **Protocoles supportés** : MediaMTX configuré pour RTSP (:8554), RTMP (:1935), SRT (:8890), HLS (:8888), WebRTC (:8189).

### Livrables créés
- ✅ `docker-compose.yml` — Configuration Docker Compose avec services MediaMTX, Redis, PostgreSQL
- ✅ `ingestion/mediamtx.yml` — Configuration MediaMTX avec endpoints RTSP/RTMP/SRT
- ✅ `ai-pipeline/simulator/` — Scripts de simulation (simulate-los.ps1, simulate-blos.ps1, simulate-los.sh, simulate-blos.sh)
- ✅ `ai-pipeline/simulator/generate-test-video.ps1` — Script de génération de vidéo de test
- ✅ `ai-pipeline/simulator/README.md` — Documentation du simulateur
- ✅ `data/test-video.mp4` — Vidéo de test générée (30s, 1280x720, 30fps)
- ✅ MediaMTX fonctionnel et recevant les flux RTMP sur `rtmp://localhost:1935/drone-01-los` et `rtmp://localhost:1935/drone-01-blos`
- ✅ Interface web MediaMTX accessible sur http://localhost:8888

### DoD (Definition of Done)
✅ **Validé** : Les flux test sont reçus par MediaMTX et accessibles via l'interface web (http://localhost:8888). Les deux modes LOS et BLOS sont simulés avec succès via RTMP.

---

## Phase 2 — Pipeline de détection de base ✅

### Objectif
Service Python qui consomme le flux MediaMTX, exécute YOLO, affiche les bboxes.

### Tâches
- [x] Service Python de consommation du flux (OpenCV/GStreamer)
- [x] Intégration YOLO (personnes/véhicules)
- [x] Intégration SAHI pour petits objets
- [x] Affichage des bboxes (fenêtre OpenCV)
- [x] Mesure et documentation du FPS d'inférence

### Décisions techniques prises
- **YOLOv8n** : Modèle nano choisi pour CPU (rapide, ~3-4 FPS sur CPU standard)
- **SAHI** : Intégré et corrigé pour SAHI 0.12+ (model_type="ultralytics", get_sliced_prediction)
  - **Note (2026-06-27)** : SAHI fonctionne correctement mais désactivé par défaut sur CPU (0.13 FPS)
  - Sur CPU : 3.68 FPS sans SAHI vs 0.13 FPS avec SAHI (slicing trop coûteux)
  - Sur GPU : SAHI recommandé pour améliorer la détection des petits objets vus d'altitude
- **OpenCV** : Utilisé pour la consommation du flux RTSP et l'affichage des bounding boxes
- **Configuration flexible** : Classe DetectionConfig avec variables d'environnement supportées
- **Classes détectées** : person, bicycle, car, motorcycle, truck, bus (COCO)
- **Couleurs d'affichage** : Vert pour personnes, Rouge pour véhicules, Jaune pour vélos

### Livrables créés
- ✅ `ai-pipeline/inference/requirements.txt` — Dépendances Python (ultralytics, opencv-python, sahi, torch, etc.)
- ✅ `ai-pipeline/inference/config.py` — Configuration de détection (seuils, modèles, device)
- ✅ `ai-pipeline/inference/detector.py` — Service principal de détection avec YOLO
- ✅ `ai-pipeline/inference/__init__.py` — Exports publics du module
- ✅ `ai-pipeline/inference/tests/test_detector.py` — Tests unitaires basiques
- ✅ `ai-pipeline/inference/README.md` — Documentation du module
- ✅ `ai-pipeline/inference/test_detector_cli.py` — Script de validation sans GUI

### Résultats du test
- **Flux** : rtsp://localhost:8554/drone-01-los (MediaMTX)
- **Frames traitées** : 30/30
- **FPS sans SAHI** : 3.68 FPS (CPU standard, YOLOv8n)
- **FPS avec SAHI** : 0.13 FPS (CPU standard, YOLOv8n + slicing)
- **Détections** : 0 (vidéo de test vide - normal)
- **Statut** : Pipeline technique fonctionnel

### DoD
✅ **Validé** : Le pipeline de détection fonctionne correctement. SAHI intégré et corrigé pour compatibilité 0.12+. FPS acceptable sans SAHI (3.68 FPS). SAHI désactivé par défaut sur CPU (trop lent), à activer sur GPU pour améliorer détection petits objets.

### Points à améliorer
- Tester avec une vraie vidéo aérienne (dataset VisDrone) pour valider les détections visuelles (Phase 9)

---

## Phase 3 — Tracking & logique de zones ✅

### Objectif
Intégrer ByteTrack et implémenter les zones d'intrusion et regroupement.

### Tâches
- [x] Intégration ByteTrack pour track_id stables
- [x] Implémentation CRUD des zones (mémoire ou JSON)
- [x] Détection d'intrusion (centroïde dans zone)
- [x] Logique de regroupement (comptage par zone/fenêtre temporelle)
- [x] Tests unitaires sur la logique de zones/regroupement
- [x] Intégration du tracking dans le pipeline de détection principal

### Décisions techniques prises
- **ByteTrack intégré via Ultralytics** : Utilisation de l'intégration native d'Ultralytics YOLOv8 avec `model.track(persist=True)` au lieu d'une implémentation séparée
- **Module tracking** : Créé `ai-pipeline/tracking/tracker.py` avec classe `MultiObjectTracker` pour gérer les tracks (historique, vélocité, nettoyage)
- **Module zones** : Créé `ai-pipeline/zones/zone_manager.py` avec Shapely pour les calculs géométriques (BSD licence)
- **Module crowd detector** : Créé `ai-pipeline/zones/crowd_detector.py` pour la détection de regroupement avec fenêtre temporelle
- **Types de zones** : INTRUSION, CROWD, SAFE
- **Configuration tracking** : Ajouté `use_tracking` et `tracker_type` dans `DetectionConfig`
- **Affichage** : Les track_id sont affichés dans les labels des bounding boxes

### Livrables créés
- ✅ `ai-pipeline/tracking/tracker.py` — Module de tracking multi-objets
- ✅ `ai-pipeline/tracking/requirements.txt` — Dépendances tracking
- ✅ `ai-pipeline/tracking/README.md` — Documentation du module
- ✅ `ai-pipeline/tracking/tests/test_tracker.py` — Tests unitaires tracking (6 tests passés)
- ✅ `ai-pipeline/zones/zone_manager.py` — Gestionnaire de zones avec Shapely
- ✅ `ai-pipeline/zones/crowd_detector.py` — Détecteur de regroupement
- ✅ `ai-pipeline/zones/requirements.txt` — Dépendances zones (shapely)
- ✅ `ai-pipeline/zones/README.md` — Documentation du module
- ✅ `ai-pipeline/zones/tests/test_zone_manager.py` — Tests unitaires zones (14 tests passés)
- ✅ `ai-pipeline/zones/tests/test_crowd_detector.py` — Tests unitaires crowd (8 tests passés)
- ✅ `ai-pipeline/inference/config.py` — Ajout configuration tracking (use_tracking, tracker_type)
- ✅ `ai-pipeline/inference/detector.py` — Intégration tracking YOLO + affichage track_id

### Résultats des tests
- **Tests tracking** : 6/6 passés
- **Tests zones** : 14/14 passés
- **Tests crowd detector** : 8/8 passés
- **Total tests Phase 3** : 28/28 passés

### DoD
✅ **Validé** : Tests unitaires sur la logique de zones/regroupement avec scénarios simulés. Tracking intégré dans le pipeline principal.

---

## Phase 4 — Classification de déplacement ✅

### Objectif
Distinguer piéton vs moto par association personne↔véhicule et vitesse.

### Tâches
- [x] Association personne ↔ moto entre frames
- [x] Calcul de vitesse relative
- [x] Classification du mode de déplacement
- [x] Tests unitaires sur la logique de classification
- [x] Intégration dans le pipeline principal

### Décisions techniques prises
- **Calcul de vitesse** : Ajout de `get_average_speed()` dans TrackedObject pour calculer la vitesse moyenne en pixels/frame à partir de l'historique des positions
- **Association personne↔moto** : Utilisation de deux critères :
  - Distance centroïde < seuil (configurable, défaut 100 pixels)
  - IoU > seuil (configurable, défaut 0.1)
- **Stabilité temporelle** : L'association nécessite N frames consécutives (configurable via `min_association_frames`, défaut 5) pour confirmer qu'une personne est sur une moto
- **Classification** :
  - `MOTORBIKE` : Association stable avec une moto détectée
  - `FOOT` : Pas d'association moto, classification basée sur la vitesse
    - Marche normale : vitesse < seuil de marche (2 pixels/frame)
    - Marche rapide : vitesse > seuil rapide (5 pixels/frame)
- **Limitation** : Sans télémétrie GPS/altitude, la vitesse est en pixels/frame et non en m/s — documenté dans README
- **Intégration automatique** : La classification est activée automatiquement quand `use_tracking=True` dans DetectionConfig

### Livrables créés
- ✅ `ai-pipeline/tracking/tracker.py` — Ajout méthode `get_average_speed()` dans TrackedObject
- ✅ `ai-pipeline/tracking/movement_classifier.py` — Module de classification de mouvement (MovementClassifier, MovementType, MovementClassification)
- ✅ `ai-pipeline/tracking/tests/test_movement_classifier.py` — Tests unitaires (13 tests passés)
- ✅ `ai-pipeline/inference/detector.py` — Intégration classification (ajout champ `movement_type` dans Detection, affichage dans labels)
- ✅ `ai-pipeline/tracking/README.md` — Documentation mise à jour avec classification de mouvement

### Résultats des tests
- **Tests movement_classifier** : 13/13 passés
  - Test initialisation
  - Test classification sans tracks
  - Test classification personne seule
  - Test classification avec moto proche
  - Test association stable moto
  - Test classification vitesse marche
  - Test classification vitesse rapide
  - Test classification multiple personnes
  - Test calcul IoU
  - Test reset
  - Test nettoyage historique
  - Test vitesse insuffisante
  - Test vitesse suffisante

### DoD
✅ **Validé** : Tests unitaires sur la logique de classification avec scénarios simulés. Classification intégrée dans le pipeline principal. Le système distingue piéton vs moto via association stable et analyse de vitesse.

### Points à améliorer
- Tester avec une vraie vidéo aérienne contenant des personnes à moto pour valider la classification visuelle (Phase 9)
- Ajuster les seuils de distance et IoU empiriquement sur des cas réels
- Ajouter la possibilité de convertir pixels/frame en m/s si télémétrie GPS/altitude disponible

---

---

## Phase 5 — Détection d'armes ✅

### Objectif
Entraîner un modèle dédié pour la détection d'armes avec confirmation opérateur.

### Dataset
- **Source** : Weapon_Detection_for_Yolo (Kaggle) — dataset complet pré-annoté, format YOLO
- **Décision** : Sourcing/labellisation manuelle via CVAT abandonnée au profit de ce dataset public déjà annoté
- **Statistiques** :
  - Train: 18,186 images
  - Val: 4,546 images
  - Test: 623 images
  - Classes: 1 (Weapon)

### Tâches
- [x] Validation du dataset (intégrité des fichiers, classes, structure des annotations, splits train/val/test)
- [x] Vérification de compatibilité du format avec Ultralytics CLI (ajustement du `data.yaml`)
- [x] Entraînement avec Ultralytics CLI
- [x] Évaluation (precision/recall, matrice de confusion)
- [x] Intégration avec seuil de confiance élevé + flag "à confirmer"
- [x] Logique de zoom de confirmation (si matériel le permet) — documenté comme limitation

### Décisions techniques prises
- **Dataset** : Weapon_Detection_for_Yolo (Kaggle) utilisé tel quel plutôt qu'un labelling CVAT manuel, pour gagner du temps et bénéficier d'un volume d'images plus important
- **Entraînement CPU** : Test technique avec 1 epoch sur subset (500 train, 100 val) car entraînement complet sur CPU prendrait plusieurs heures
  - Pour production : GPU NVIDIA requis avec 100+ epochs sur dataset complet
- **Limite connue à documenter** : ce dataset est probablement constitué d'images au sol (caméras classiques), pas de vues aériennes/drone — un écart de domaine (angle, échelle, résolution) est à anticiper et à valider en Phase 9 avec de vraies images aériennes
- **Seuil de confiance** : 0.8 pour minimiser les faux positifs
- **Flag de confirmation** : Toute détection d'arme est marquée `requires_confirmation=True` pour confirmation obligatoire par l'opérateur

### Livrables créés
- ✅ `ai-pipeline/training/` — Module d'entraînement complet (train.py, evaluate.py, requirements.txt, README.md)
- ✅ `ai-pipeline/training/tests/test_train.py` — Tests unitaires dataset (3/3 passés)
- ✅ `datasets/dataset_merged/data.yaml` — Configuration dataset avec chemin absolu
- ✅ `datasets/dataset_merged/data_test.yaml` — Configuration subset pour test CPU
- ✅ `datasets/dataset_merged/train_subset/` — Subset 500 images pour test rapide
- ✅ `datasets/dataset_merged/val_subset/` — Subset 100 images pour test rapide
- ✅ `ai-pipeline/models/weapon_detection.pt` — Modèle entraîné (test technique)
- ✅ `docs/weapon-detection-report.md` — Rapport de performance détaillé
- ✅ `ai-pipeline/inference/config.py` — Ajout configuration modèle armes (weapon_model_path, weapon_confidence_threshold)
- ✅ `ai-pipeline/inference/detector.py` — Intégration détection armes (_detect_weapons, flag requires_confirmation)

### Résultats du test technique (CPU, 1 epoch, subset)
- **mAP50** : 6.25%
- **mAP50-95** : 2.13%
- **Precision** : 2.48%
- **Recall** : 50.97%
- **F1 Score** : 4.73%
- **Temps d'entraînement** : ~14 minutes
- **Vitesse inférence** : ~4 FPS sur CPU

**Note** : Ces métriques sont faibles mais attendues pour 1 epoch sur subset. Le pipeline technique fonctionne et est prêt pour un entraînement complet sur GPU.

### DoD
✅ **Validé** : Rapport de performance du modèle versionné dans `docs/weapon-detection-report.md`, métriques explicites, et limites documentées (notamment l'écart potentiel entre le dataset Kaggle au sol et le cas d'usage réel vue-drone).

### Points à améliorer
- Entraînement complet sur GPU (100+ epochs, dataset complet 18,186 images)
- Fine-tuning sur images aériennes/drone pour réduire l'écart de domaine
- Intégration SAHI pour améliorer la détection de petits objets vus d'altitude
- Validation sur vraies images aériennes en Phase 9

---

## Phase 6 — Moteur de règles & alertes ⏸️

### Objectif
Centraliser la logique métier et publier les événements sur Redis/MQTT.

### Tâches
- [ ] Module centralisé de règles métier
- [ ] Gestion des priorités et anti-spam/cooldown
- [ ] Publication événements sur Redis/MQTT (JSON standardisé)
- [ ] Tests d'intégration (rafale d'événements, vérification anti-spam)

### DoD
Tests d'intégration simulant une rafale d'événements, vérification de l'anti-spam.

---

## Phase 7 — Backend API ⏸️

### Objectif
FastAPI avec endpoints REST et WebSocket pour les alertes temps réel.

### Tâches
- [ ] Endpoints REST (zones, événements, drones)
- [ ] WebSocket `/ws/alerts`
- [ ] Persistance PostgreSQL via Alembic
- [ ] Swagger/OpenAPI généré et navigable

### DoD
Swagger/OpenAPI généré et navigable, événements persistés et requêtables.

---

## Phase 8 — Dashboard Web ⏸️

### Objectif
Interface React avec carte, vidéo live, alertes et replay.

### Tâches
- [ ] Vue carte (Leaflet, tuiles locales) avec position drones et zones
- [ ] Vue vidéo live (WebRTC) avec overlay détections
- [ ] Panneau d'alertes (liste, filtres, accusé réception) + sons
- [ ] Mode replay (clic alerte → relecture clip ±10s)

### DoD
Démonstration manuelle complète du flux alerte → son → visuel → clic → replay.

---

## Phase 9 — Intégration bout-en-bout ⏸️

### Objectif
Test complet avec vidéo aérienne réaliste et mesure de latence.

### Tâches
- [ ] Test avec dataset VisDrone/UAVDT ou enregistrement réel
- [ ] Mesure latence bout-en-bout
- [ ] Rapport de test avec latence et taux de détection

### DoD
Rapport de test avec latence mesurée et taux de détection sur le jeu de test.

---

## Phase 10 — Sécurisation & déploiement ⏸️

### Objectif
Authentification, TLS local, Docker Compose final et documentation.

### Tâches
- [ ] Authentification dashboard (compte opérateur)
- [ ] TLS local (mkcert) sur Nginx
- [ ] docker-compose.yml final
- [ ] Scripts d'installation
- [ ] Documentation runbook.md (démarrage, arrêt, sauvegarde, supervision)

### DoD
Déploiement complet en une commande (`docker compose up -d`) sur machine propre, checklist finale validée.
