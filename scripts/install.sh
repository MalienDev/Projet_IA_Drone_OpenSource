#!/bin/bash
# Script d'installation pour le système de surveillance par drone (Linux)
# Usage: ./scripts/install.sh

set -e

echo "========================================"
echo "Installation - Drone Surveillance System"
echo "========================================"
echo ""

# Vérifier Docker
echo "🔍 Vérification de Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker est installé"
else
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

# Vérifier Docker Compose
echo "🔍 Vérification de Docker Compose..."
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose est installé"
else
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Vérifier OpenSSL
echo "🔍 Vérification d'OpenSSL..."
if command -v openssl &> /dev/null; then
    echo "✅ OpenSSL est installé"
else
    echo "⚠️ OpenSSL n'est pas installé. Les certificats TLS ne seront pas générés."
fi

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
    echo "⚠️ Veuillez éditer .env avec vos configurations avant de continuer"
else
    echo "✅ Fichier .env existe déjà"
fi

# Générer les certificats TLS
echo ""
echo "🔐 Génération des certificats TLS..."
if [ -f "infra/certs/generate-certs.sh" ]; then
    chmod +x infra/certs/generate-certs.sh
    ./infra/certs/generate-certs.sh
else
    echo "⚠️ Script de génération de certificats non trouvé"
fi

# Créer les répertoires de données
echo ""
echo "📁 Création des répertoires de données..."
mkdir -p data/media/snapshots
mkdir -p data/media/clips
mkdir -p data/tiles
mkdir -p data/mediamtx
echo "✅ Répertoires créés"

# Télécharger le modèle YOLOv8n s'il n'existe pas
echo ""
echo "📥 Téléchargement du modèle YOLOv8n..."
if [ ! -f "yolov8n.pt" ]; then
    echo "⏳ Téléchargement en cours..."
    # Le modèle sera téléchargé automatiquement par Ultralytics au premier lancement
    echo "✅ Le modèle sera téléchargé automatiquement au premier lancement"
else
    echo "✅ Modèle YOLOv8n existe déjà"
fi

# Construire les images Docker
echo ""
echo "🔨 Construction des images Docker..."
echo "⏳ Cela peut prendre plusieurs minutes..."
docker compose build

echo ""
echo "========================================"
echo "✅ Installation terminée avec succès !"
echo "========================================"
echo ""
echo "Pour démarrer le système :"
echo "  docker compose up -d"
echo ""
echo "Pour arrêter le système :"
echo "  docker compose down"
echo ""
echo "Dashboard disponible sur :"
echo "  HTTP :  http://localhost:3000"
echo "  HTTPS : https://localhost:3443"
echo ""
