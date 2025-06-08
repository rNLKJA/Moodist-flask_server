#!/bin/bash
# Script to verify SSL certificates

# Check if certificates exist
if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
    echo "Error: Certificate files not found. Please run ./scripts/generate_certs.sh first."
    exit 1
fi

# Verify certificate
echo "Verifying certificate..."
openssl verify -CAfile certs/rootCA.pem certs/cert.pem

# Check certificate expiration
echo "Checking certificate expiration..."
EXPIRY=$(openssl x509 -enddate -noout -in certs/cert.pem | cut -d= -f2)
echo "Certificate expires on: $EXPIRY"

# Display certificate information
echo "Certificate information:"
openssl x509 -in certs/cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before:|Not After :|DNS:"

# Check if the certificate has the right Subject Alternative Names
echo "Checking Subject Alternative Names..."
if openssl x509 -in certs/cert.pem -text -noout | grep -q "DNS:localhost"; then
    echo "Certificate includes localhost as a Subject Alternative Name ✓"
else
    echo "Warning: Certificate does not include localhost as a Subject Alternative Name"
fi 