# Frontend - Drone Surveillance Dashboard

Interface React pour le système de surveillance par drone.

## Stack technique

- **React 18** avec TypeScript
- **Vite** pour le build
- **TailwindCSS** pour le styling
- **React Router** pour la navigation
- **Leaflet + react-leaflet** pour la carte
- **Axios** pour les appels API
- **Howler.js** pour les sons d'alerte

## Installation

```bash
npm install
```

## Développement

```bash
npm run dev
```

Le serveur de développement démarre sur http://localhost:3000

## Build pour production

```bash
npm run build
```

## Structure du projet

```
src/
├── components/       # Composants React
│   ├── MapView.tsx         # Carte Leaflet avec tuiles locales
│   ├── VideoPlayer.tsx     # Lecteur vidéo WebRTC
│   ├── AlertPanel.tsx      # Panneau d'alertes avec WebSocket
│   └── VideoReplay.tsx     # Modal de replay des clips
├── hooks/           # Hooks personnalisés
│   ├── useAuth.ts          # Gestion authentification
│   ├── useAlerts.ts        # Abonnement WebSocket alertes
│   ├── useDrones.ts        # Récupération drones
│   └── useZones.ts         # Récupération zones
├── pages/           # Pages
│   ├── LoginPage.tsx       # Page de login
│   └── DashboardPage.tsx   # Dashboard principal
├── services/        # Services API
│   └── api.ts              # Client Axios avec intercepteurs
├── types/           # Types TypeScript
│   └── index.ts            # Types communs
├── App.tsx          # Composant principal
├── main.tsx         # Point d'entrée
└── index.css        # Styles globaux
```

## Fonctionnalités

### Authentification
- Login JWT avec token stocké dans localStorage
- Protection des routes avec `useAuth`
- Auto-logout sur token invalide (401)

### Carte (MapView)
- Affichage des drones avec marqueurs
- Affichage des zones avec polygones colorés
- Tuiles OSM locales via TileServer-GL (http://localhost:8080)
- Fallback vers tuiles externes en développement

### Vidéo (VideoPlayer)
- Streaming WebRTC depuis MediaMTX (http://localhost:8189)
- Indicateur de connexion LIVE
- Gestion des erreurs de connexion

### Alertes (AlertPanel)
- Abonnement WebSocket temps réel
- Liste des alertes avec filtres
- Sons d'alerte avec Howler.js
- Bouton d'accusé de réception
- Affichage des snapshots
- Bouton de replay des clips

### Replay (VideoReplay)
- Modal de lecture des clips vidéo enregistrés
- Contrôles vidéo natifs

## Configuration

Variables d'environnement (optionnelles) :
- `VITE_API_URL` : URL de l'API backend (défaut: http://localhost:8000)

## Docker

Le frontend est conteneurisé avec nginx :

```bash
docker build -t drone-surveillance-frontend .
docker run -p 3000:80 drone-surveillance-frontend
```

Ou via docker-compose :

```bash
docker compose up frontend
```

## Points d'attention

- Les tuiles OSM locales nécessitent TileServer-GL avec un fichier mbtiles dans `data/tiles/`
- Le streaming WebRTC nécessite MediaMTX configuré correctement
- Les sons d'alerte nécessitent un fichier `/sounds/alert.mp3` dans le dossier public
- Le WebSocket nécessite un token JWT valide en paramètre

## Prochaines améliorations

- [ ] Ajouter filtres avancés sur les alertes
- [ ] Mode plein écran pour la vidéo
- [ ] Historique des alertes paginé
- [ ] Éditeur de zones sur la carte
- [ ] Graphiques de statistiques
