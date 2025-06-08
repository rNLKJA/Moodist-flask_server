#!/bin/bash

# Let's Encrypt Certificate Setup for Globally Trusted HTTPS
# Requires: Domain name pointing to your server

set -e  # Exit on any error

echo "🌍 Setting up Let's Encrypt Globally Trusted Certificates"
echo "========================================================"

# Check for required parameters
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <domain-name> [email]"
    echo "   Example: $0 api.moodist.com user@example.com"
    echo ""
    echo "📋 Prerequisites:"
    echo "   - Domain name must point to this server's IP"
    echo "   - Port 80 must be accessible (for verification)"
    echo "   - Server must be publicly accessible"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"your-email@example.com"}

echo "📍 Configuration:"
echo "   - Domain: $DOMAIN"
echo "   - Email: $EMAIL"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing Certbot..."
    
    # Detect OS and install certbot
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install certbot
        else
            echo "❌ Please install Homebrew first: https://brew.sh"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot
        else
            echo "❌ Please install certbot manually"
            exit 1
        fi
    else
        echo "❌ Unsupported operating system. Please install certbot manually."
        exit 1
    fi
fi

echo "✅ Certbot installed"

# Stop any running server on port 80 (required for verification)
echo "🛑 Stopping any services on port 80..."
sudo lsof -ti:80 | xargs sudo kill -9 2>/dev/null || true

# Request certificate using standalone mode
echo "🔐 Requesting Let's Encrypt certificate for $DOMAIN..."
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN"

# Check if certificate was created
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
if [[ -f "$CERT_PATH/fullchain.pem" && -f "$CERT_PATH/privkey.pem" ]]; then
    echo "✅ Certificate successfully created!"
    
    # Copy certificates to our certs directory
    echo "📂 Copying certificates to certs/ directory..."
    sudo cp "$CERT_PATH/fullchain.pem" "certs/global-cert.pem"
    sudo cp "$CERT_PATH/privkey.pem" "certs/global-key.pem"
    
    # Fix permissions
    sudo chown $(whoami):$(whoami) certs/global-cert.pem certs/global-key.pem
    chmod 644 certs/global-cert.pem
    chmod 600 certs/global-key.pem
    
    echo "✅ Certificates copied to:"
    echo "   - certs/global-cert.pem"
    echo "   - certs/global-key.pem"
else
    echo "❌ Certificate creation failed!"
    echo "   Make sure:"
    echo "   - Domain $DOMAIN points to this server"
    echo "   - Port 80 is accessible from the internet"
    echo "   - No firewall is blocking the connection"
    exit 1
fi

# Create renewal script
echo "🔄 Setting up automatic renewal..."
cat > scripts/renew_letsencrypt.sh << EOF
#!/bin/bash
# Auto-renewal script for Let's Encrypt certificates

echo "🔄 Renewing Let's Encrypt certificates..."
sudo certbot renew --quiet

# Copy renewed certificates
if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "certs/global-cert.pem"
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "certs/global-key.pem"
    sudo chown \$(whoami):\$(whoami) certs/global-cert.pem certs/global-key.pem
    chmod 644 certs/global-cert.pem
    chmod 600 certs/global-key.pem
    echo "✅ Certificates renewed and copied"
fi
EOF

chmod +x scripts/renew_letsencrypt.sh

echo ""
echo "🎉 Let's Encrypt setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Update your .env file to use global certificates:"
echo "      SSL_CERT=certs/global-cert.pem"
echo "      SSL_KEY=certs/global-key.pem"
echo ""
echo "   2. Start your server:"
echo "      ./scripts/start_production.sh"
echo ""
echo "   3. Access your API at: https://$DOMAIN"
echo ""
echo "🔄 Certificate renewal:"
echo "   - Certificates auto-renew in 90 days"
echo "   - Test renewal: sudo certbot renew --dry-run"
echo "   - Manual renewal: ./scripts/renew_letsencrypt.sh"
echo ""
echo "💡 Add to crontab for automatic renewal:"
echo "   0 2 * * * /path/to/your/project/scripts/renew_letsencrypt.sh" 