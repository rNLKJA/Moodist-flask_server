#!/bin/bash
# Script to start the production server with Gunicorn using trusted certificates

# Load environment variables if .env file exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Check for required trusted certificates
if [[ ! -f "certs/trusted-cert.pem" || ! -f "certs/trusted-key.pem" ]]; then
    echo "❌ Trusted certificates not found!"
    echo "   Please run: mkcert -install && mkcert localhost 127.0.0.1 ::1 YOUR_IP"
    echo "   Then copy the certificates to certs/trusted-cert.pem and certs/trusted-key.pem"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Set default environment variables if not set
export FLASK_CONFIG=${FLASK_CONFIG:-production}
export FLASK_APP=${FLASK_APP:-wsgi.py}
export GUNICORN_BIND=${GUNICORN_BIND:-0.0.0.0:8000}
export GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
export GUNICORN_LOG_LEVEL=${GUNICORN_LOG_LEVEL:-info}

# Print server information
echo "🚀 Starting Moodist in PRODUCTION mode..."
echo "📍 Configuration:"
echo "   - Binding to: $GUNICORN_BIND"
echo "   - Workers: $GUNICORN_WORKERS"
echo "   - Log level: $GUNICORN_LOG_LEVEL"
echo "   - SSL/HTTPS: enabled (trusted certificates)"
echo "   - Network accessible: Yes"
echo ""

# Start Gunicorn with trusted TLS/SSL certificates
exec gunicorn \
  --config gunicorn_config.py \
  --bind $GUNICORN_BIND \
  --workers $GUNICORN_WORKERS \
  --certfile certs/trusted-cert.pem \
  --keyfile certs/trusted-key.pem \
  wsgi:app 