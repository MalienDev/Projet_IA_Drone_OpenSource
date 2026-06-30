const fs = require('fs');
const { execSync } = require('child_process');

const certDir = __dirname;

console.log('Generating TLS certificates...');

try {
  // Generate private key
  execSync('openssl genrsa -out key.pem 2048', { cwd: certDir });
  
  // Generate self-signed certificate
  execSync('openssl req -new -x509 -key key.pem -out cert.pem -days 365 -subj "/C=FR/ST=State/L=City/O=DroneSurveillance/CN=localhost"', { cwd: certDir });
  
  console.log('Certificates generated successfully:');
  console.log('  - key.pem');
  console.log('  - cert.pem');
} catch (error) {
  console.error('Error generating certificates:', error.message);
  console.log('Trying alternative method with Node.js crypto module...');
  
  // Fallback: generate using Node.js crypto
  const crypto = require('crypto');
  
  const key = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  
  fs.writeFileSync(`${certDir}/key.pem`, key.privateKey);
  
  const cert = crypto.createCertificate({
    hash: 'sha256',
    subject: {
      countryName: 'FR',
      stateOrProvinceName: 'State',
      localityName: 'City',
      organizationName: 'DroneSurveillance',
      commonName: 'localhost'
    },
    issuer: {
      countryName: 'FR',
      stateOrProvinceName: 'State',
      localityName: 'City',
      organizationName: 'DroneSurveillance',
      commonName: 'localhost'
    },
    serial: 1n,
    notBefore: new Date(),
    notAfter: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
    privateKey: key.privateKey,
    publicKey: key.publicKey,
    extensions: [
      { name: 'subjectAltName', altNames: [{ type: 2, value: 'localhost' }] }
    ]
  });
  
  fs.writeFileSync(`${certDir}/cert.pem`, cert.toString());
  
  console.log('Certificates generated successfully (Node.js fallback):');
  console.log('  - key.pem');
  console.log('  - cert.pem');
}
