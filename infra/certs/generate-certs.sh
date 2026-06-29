#!/bin/bash
# Script de génération de certificats auto-signés pour TLS local
# Usage: ./generate-certs.sh

CERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$CERT_DIR"

echo "🔐 Génération des certificats TLS auto-signés..."

# Générer la clé privée
openssl genrsa -out "$CERT_DIR/key.pem" 2048

# Générer le certificat auto-signé
openssl req -new -x509 -key "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem" -days 365 \
  -subj "/C=FR/ST=State/L=City/O=DroneSurveillance/CN=localhost"

# Générer un certificat pour le frontend
openssl req -new -x509 -key "$CERT_DIR/key.pem" -out "$CERT_DIR/frontend-cert.pem" -days 365 \
  -subj "/C=FR/ST=State/L=City/O=DroneSurveillance/CN=localhost"

echo "✅ Certificats générés avec succès :"
echo "   - $CERT_DIR/key.pem"
echo "   - $CERT_DIR/cert.pem"
echo "   - $CERT_DIR/frontend-cert.pem"
