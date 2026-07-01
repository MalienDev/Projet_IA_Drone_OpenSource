# Module d'Intégration Bout-en-Bout

Ce module contient les scripts et outils pour tester l'intégration complète du pipeline de surveillance par drone.

## Objectif

Valider le flux complet du système :
1. **Ingestion** : Simulateur FFmpeg → MediaMTX
2. **Pipeline IA** : Détection + Tracking + Règles
3. **Publication** : Redis (optionnel)
4. **Mesure** : Latence et FPS

## Structure

```
ai-pipeline/integration/
├── __init__.py
├── integration_test.py  # Script principal de test
├── real_video_e2e.py    # Test local complet avec vraie video drone
├── requirements.txt
└── README.md
```

## Usage

### Test basique avec la vidéo synthétique

```bash
cd ai-pipeline/integration
python integration_test.py --video ../../test-video.mp4 --duration 30
```

### Test avec une vraie vidéo aérienne

```bash
python integration_test.py --video /path/to/aerial-video.mp4 --duration 60
```

### Test reel bout-en-bout avec VisDrone

Depuis la racine du depot, avec Docker Compose deja lance :

```powershell
python ai-pipeline\integration\real_video_e2e.py --video data\visdrone_test_video.mp4 --duration 30
```

Ce test boucle la video vers MediaMTX, verifie le HLS, execute YOLO + ByteTrack,
publie les alertes Redis, verifie leur persistance backend, puis genere :

- `docs/real-video-e2e-report.json`
- `docs/real-video-e2e-report.md`

Le profil par defaut est CPU : SAHI et le modele armes sont desactives pour garder
un test local rapide. Toute detection d'arme reste a confirmer par l'operateur si
le modele armes est active explicitement.

## Paramètres

- `--video` : Chemin vers la vidéo de test (défaut: `test-video.mp4`)
- `--duration` : Durée du test en secondes (défaut: 30)
- `--use-sahi` : Active SAHI pour petits objets, recommande seulement sur GPU
- `--enable-weapon-model` : Active le modele armes, confirmation operateur obligatoire

## Résultats

Le script génère :
1. **Sortie console** : Statistiques en temps réel (FPS, détections, alertes)
2. **Rapport JSON** : `docs/integration-test-report.json` avec :
   - Latences moyennes/min/max
   - FPS effectif
   - Nombre de détections et alertes
   - Limitations et recommandations

## Limitations actuelles

- **Vidéo synthétique** : La vidéo de test actuelle est générée par FFmpeg (écran noir), pas de vraies scènes aériennes
- **Pas de Redis réel** : Les alertes ne sont pas publiées sur Redis dans le test actuel
- **Test CPU uniquement** : SAHI désactivé (trop lent sur CPU)
- **Latence partielle** : Mesure uniquement la détection IA, pas la latence réseau/dashboard

## Recommandations pour un test complet

1. **Dataset aérien** : Utiliser un vrai dataset (VisDrone, UAVDT) ou un enregistrement réel
2. **Redis actif** : Démarrer Redis et activer `enable_alert_publishing=True`
3. **GPU disponible** : Activer SAHI pour améliorer la détection des petits objets
4. **Mesure complète** : Ajouter des timestamps côté dashboard pour mesurer la latence bout-en-bout

## Prochaines étapes

- [ ] Télécharger un dataset VisDrone ou UAVDT
- [ ] Configurer TileServer-GL avec de vraies tuiles OSM
- [ ] Tester avec Redis actif
- [ ] Mesurer la latence jusqu'au dashboard WebSocket
- [ ] Générer un rapport complet avec recommandations
