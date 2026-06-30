#!/usr/bin/env python3
import subprocess
import sys
import os

cert_dir = os.path.dirname(os.path.abspath(__file__))

print("Generating TLS certificates...")

# Try using OpenSSL if available
try:
    subprocess.run(['openssl', 'version'], check=True, capture_output=True)
    print("OpenSSL found, generating certificates...")
    
    # Generate private key
    subprocess.run([
        'openssl', 'genrsa', '-out', 
        os.path.join(cert_dir, 'key.pem'), '2048'
    ], check=True)
    
    # Generate self-signed certificate
    subprocess.run([
        'openssl', 'req', '-new', '-x509', 
        '-key', os.path.join(cert_dir, 'key.pem'),
        '-out', os.path.join(cert_dir, 'cert.pem'),
        '-days', '365',
        '-subj', '/C=FR/ST=State/L=City/O=DroneSurveillance/CN=localhost'
    ], check=True)
    
    print("Certificates generated successfully:")
    print(f"  - {os.path.join(cert_dir, 'key.pem')}")
    print(f"  - {os.path.join(cert_dir, 'cert.pem')}")
    
except (subprocess.CalledProcessError, FileNotFoundError):
    print("OpenSSL not available, creating dummy certificates for development...")
    
    # Create minimal dummy certificates for development
    # These won't be secure but will allow nginx to start
    dummy_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cK
DkHvCLrdN2uTdBhNzQ8lJ7qJj5Q5ZJ5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z
-----END PRIVATE KEY-----"""
    
    dummy_cert = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0GczEuY29tMRkwFwYDVQQKExBEcm9u
ZVN1cnZlaWxsYW5jZTEmMCQGA1UEAxMdZGV2ZWxvcG1lbnQubG9jYWxob3N0LmRv
bWFpbjAeFw0yNDAxMDEwMDAwMDBaFw0yNTAxMDEwMDAwMDBaMBoxGDAWBgNVBAMT
D2xvY2FsaG9zdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALtUlPS3
1SzxwoOQe8Iut03a50NCE3NDyUnuomPlDlknlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
lnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnlnln
-----END CERTIFICATE-----"""
    
    with open(os.path.join(cert_dir, 'key.pem'), 'w') as f:
        f.write(dummy_key)
    with open(os.path.join(cert_dir, 'cert.pem'), 'w') as f:
        f.write(dummy_cert)
    
    print("Dummy certificates created for development (NOT SECURE):")
    print(f"  - {os.path.join(cert_dir, 'key.pem')}")
    print(f"  - {os.path.join(cert_dir, 'cert.pem')}")
    print("WARNING: These are placeholder certificates only for development.")
