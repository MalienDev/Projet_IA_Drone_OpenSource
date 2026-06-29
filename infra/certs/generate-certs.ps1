# Script de génération de certificats auto-signés pour TLS local (Windows)
# Usage: .\generate-certs.ps1

$ErrorActionPreference = "Stop"

$CertDir = $PSScriptRoot
New-Item -ItemType Directory -Force -Path $CertDir | Out-Null

Write-Host "🔐 Génération des certificats TLS auto-signés..." -ForegroundColor Green

# Générer la clé privée
openssl genrsa -out "$CertDir\key.pem" 2048

# Générer le certificat auto-signé
openssl req -new -x509 -key "$CertDir\key.pem" -out "$CertDir\cert.pem" -days 365 `
  -subj "/C=FR/ST=State/L=City/O=DroneSurveillance/CN=localhost"

Write-Host "✅ Certificats générés avec succès :" -ForegroundColor Green
Write-Host "   - $CertDir\key.pem"
Write-Host "   - $CertDir\cert.pem"
