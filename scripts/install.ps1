# Script d'installation pour le système de surveillance par drone (Windows)
# Usage: .\scripts\install.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation - Drone Surveillance System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Docker
Write-Host "🔍 Vérification de Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker est installé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé. Veuillez installer Docker Desktop." -ForegroundColor Red
    exit 1
}

# Vérifier Docker Compose
Write-Host "🔍 Vérification de Docker Compose..." -ForegroundColor Yellow
try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose est installé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose n'est pas installé. Veuillez installer Docker Desktop." -ForegroundColor Red
    exit 1
}

# Vérifier OpenSSL
Write-Host "🔍 Vérification d'OpenSSL..." -ForegroundColor Yellow
try {
    openssl version | Out-Null
    Write-Host "✅ OpenSSL est installé" -ForegroundColor Green
} catch {
    Write-Host "⚠️ OpenSSL n'est pas installé. Les certificats TLS ne seront pas générés." -ForegroundColor Yellow
}

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "📝 Création du fichier .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
    Write-Host "⚠️ Veuillez éditer .env avec vos configurations avant de continuer" -ForegroundColor Yellow
} else {
    Write-Host "✅ Fichier .env existe déjà" -ForegroundColor Green
}

# Générer les certificats TLS (optionnel - HTTPS non activé par défaut)
Write-Host ""
Write-Host "🔐 Génération des certificats TLS (optionnel)..." -ForegroundColor Yellow
Write-Host "⚠️ HTTPS n'est pas activé par défaut. Le système fonctionne en HTTP." -ForegroundColor Yellow
if (Test-Path "infra\certs\generate-certs.ps1") {
    $generateCerts = Read-Host "Voulez-vous générer les certificats TLS pour activer HTTPS plus tard? (y/n)"
    if ($generateCerts -eq 'y' -or $generateCerts -eq 'Y') {
        & ".\infra\certs\generate-certs.ps1"
    }
} else {
    Write-Host "⚠️ Script de génération de certificats non trouvé" -ForegroundColor Yellow
}

# Créer les répertoires de données
Write-Host ""
Write-Host "📁 Création des répertoires de données..." -ForegroundColor Yellow
$directories = @(
    "data\media\snapshots",
    "data\media\clips",
    "data\tiles",
    "data\mediamtx"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "✅ $dir" -ForegroundColor Green
}

# Télécharger le modèle YOLOv8n s'il n'existe pas
Write-Host ""
Write-Host "📥 Téléchargement du modèle YOLOv8n..." -ForegroundColor Yellow
if (-not (Test-Path "yolov8n.pt")) {
    Write-Host "⏳ Téléchargement en cours..." -ForegroundColor Yellow
    # Le modèle sera téléchargé automatiquement par Ultralytics au premier lancement
    Write-Host "✅ Le modèle sera téléchargé automatiquement au premier lancement" -ForegroundColor Green
} else {
    Write-Host "✅ Modèle YOLOv8n existe déjà" -ForegroundColor Green
}

# Construire les images Docker
Write-Host ""
Write-Host "🔨 Construction des images Docker..." -ForegroundColor Yellow
Write-Host "⏳ Cela peut prendre plusieurs minutes..." -ForegroundColor Yellow
docker compose build

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Installation terminée avec succès !" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour démarrer le système :" -ForegroundColor Green
Write-Host "  docker compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "Pour arrêter le système :" -ForegroundColor Green
Write-Host "  docker compose down" -ForegroundColor White
Write-Host ""
Write-Host "Dashboard disponible sur :" -ForegroundColor Green
Write-Host "  HTTP :  http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ HTTPS n'est pas activé par défaut. Voir runbook.md pour l'activer." -ForegroundColor Yellow
Write-Host ""
