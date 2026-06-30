# TileServer-GL - Tuiles OpenStreetMap Locales

Ce service fournit des tuiles de carte OpenStreetMap hébergées localement pour respecter la contrainte "local-first" du projet.

## Configuration

Le service TileServer-GL est configuré dans `docker-compose.yml` :

```yaml
tileserver:
  image: maptiler/tileserver-gl:latest
  container_name: drone-surveillance-tileserver
  ports:
    - "8080:8080"
  volumes:
    - ./data/tiles:/data
  command: ["--port", "8080"]
```

**Note** : TileServer-GL détecte automatiquement les fichiers `.mbtiles` dans `/data` et génère une configuration de base. Aucun fichier `config.json` manuel n'est nécessaire pour le démarrage initial.

## Téléchargement des tuiles OSM

Pour utiliser des tuiles locales, vous devez télécharger des données OpenStreetMap et les convertir au format mbtiles.

### Option 1 : Télécharger un fichier mbtiles pré-généré

1. Téléchargez un fichier mbtiles depuis une source comme :
   - [OpenMapTiles](https://openmaptiles.com/) (gratuit pour usage non-commercial)
   - [MapTiler](https://www.maptiler.com/data/) (gratuit pour usage personnel)

2. Placez le fichier `.mbtiles` dans `./data/tiles/`

3. Renommez-le en `osm.mbtiles` ou configurez le nom dans TileServer

### Option 2 : Générer vos propres tuiles avec TileMill

1. Installez [TileMill](https://tilemill-project.github.io/tilemill/)
2. Importez des données OSM (ex: depuis Geofabrik)
3. Exportez en format mbtiles
4. Placez le fichier dans `./data/tiles/`

### Option 3 : Utiliser un extract régional

1. Téléchargez un extract régional depuis [Geofabrik](https://download.geofabrik.de/)
2. Convertissez-le en mbtiles avec des outils comme `tileserver-cli`

## Structure des répertoires

```
data/tiles/
├── osm.mbtiles           # Fichier de tuiles principal
└── (autres fichiers mbtiles optionnels)
```

## Démarrage du service

```bash
docker compose up -d tileserver
```

Le service sera accessible sur http://localhost:8080

## Utilisation dans le frontend

Dans le frontend React avec Leaflet, utilisez l'URL locale :

```javascript
L.tileLayer('http://localhost:8080/data/osm/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);
```

## Développement rapide (tuiles externes)

Pour le développement rapide sans tuiles locales, vous pouvez temporairement utiliser les tuiles OSM publiques (non recommandé pour la production) :

```javascript
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);
```

**Note** : Ceci viole la contrainte "local-first" et ne doit être utilisé qu'en développement.

## Vérification

Vérifiez que le service fonctionne en visitant :
- http://localhost:8080 - Interface TileServer
- http://localhost:8080/data/osm/0/0/0.png - Test de tuile (si osm.mbtiles existe)

## Ressources

- [TileServer-GL Documentation](https://tileserver.readthedocs.io/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Geofabrik Downloads](https://download.geofabrik.de/)
