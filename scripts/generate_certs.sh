#!/bin/bash
# Script to generate SSL certificates for development

# Create directory for certificates
mkdir -p certs

# Generate RSA private key
openssl genrsa -out certs/rootCA.key 4096

# Generate self-signed root CA certificate
openssl req -x509 -new -nodes -key certs/rootCA.key -sha256 -days 1024 -out certs/rootCA.pem \
  -subj "/C=AU/ST=Victoria/L=Melbourne/O=Moodist/OU=The University of Melbourne/CN=Moodist Root CA/emailAddress=rNLKJA@moodist.local"

# Generate server private key
openssl genrsa -out certs/key.pem 2048

# Create config file for certificate request
cat > certs/cert.conf << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C=AU
ST=Victoria
L=Melbourne
O=Moodist
OU=The University of Melbourne
CN=moodist.local
emailAddress=rNLKJA@moodist.local

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = moodist.local
DNS.2 = localhost
DNS.3 = 127.0.0.1
DNS.4 = ::1
EOF

# Generate certificate signing request
openssl req -new -key certs/key.pem -out certs/cert.csr -config certs/cert.conf

# Create extension file
cat > certs/cert.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = moodist.local
DNS.2 = localhost
DNS.3 = 127.0.0.1
DNS.4 = ::1
EOF

# Generate server certificate
openssl x509 -req -in certs/cert.csr -CA certs/rootCA.pem -CAkey certs/rootCA.key \
  -CAcreateserial -out certs/cert.pem -days 825 -sha256 -extfile certs/cert.ext

# Set permissions
chmod 600 certs/key.pem certs/cert.pem

echo "Certificates generated successfully!"
echo "Root CA: certs/rootCA.pem"
echo "Server certificate: certs/cert.pem"
echo "Server key: certs/key.pem"

# Instructions for trusting the certificate
echo "----------------------------------------------------"
echo "To trust this certificate on your local machine:"
echo "----------------------------------------------------"
echo "MacOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/rootCA.pem"
echo "Linux: sudo cp certs/rootCA.pem /usr/local/share/ca-certificates/moodist-rootCA.crt && sudo update-ca-certificates"
echo "Windows: Double-click certs/rootCA.pem -> Install Certificate -> Local Machine -> Place all certificates in the following store -> Trusted Root Certification Authorities" 