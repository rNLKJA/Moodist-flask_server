#!/bin/bash

# Development startup script for Moodist Flask Server
# Automatically starts Flask + Ngrok for mobile-ready development

set -e  # Exit on any error

echo "🚀 Starting Moodist Development Environment"
echo "=========================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    source venv/bin/activate
fi

# Check for required certificates
if [[ ! -f "certs/global-cert.pem" || ! -f "certs/global-key.pem" ]]; then
    echo "❌ Certificates not found! Generating mkcert certificates..."
    
    # Check if mkcert is installed
    if ! command -v mkcert &> /dev/null; then
        echo "📦 Installing mkcert..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install mkcert
        else
            echo "Please install mkcert: https://github.com/FiloSottile/mkcert"
            exit 1
        fi
    fi
    
    # Generate certificates
    mkcert -install
    mkcert localhost 127.0.0.1 ::1
    cp localhost+*.pem certs/global-cert.pem
    cp localhost+*-key.pem certs/global-key.pem
    rm localhost+*.pem localhost+*-key.pem
    echo "✅ Certificates generated"
fi

# Check if ngrok is installed and authenticated
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok not found! Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ngrok/ngrok/ngrok
    else
        echo "Please install ngrok: https://ngrok.com/download"
        exit 1
    fi
fi

if ! ngrok config check &>/dev/null; then
    echo "❌ Ngrok not authenticated!"
    echo "   1. Go to: https://ngrok.com/signup"
    echo "   2. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "   3. Run: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

# Load environment variables
if [[ -f ".env" ]]; then
    echo "📄 Loading environment variables from .env"
    while IFS= read -r line; do
        [[ $line =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        line=$(echo "$line" | sed 's/#.*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        [[ -z "$line" ]] && continue
        export "$line"
    done < .env
fi

# Set development configuration
export FLASK_CONFIG=development
export SSL_ENABLED=true
export HOST=127.0.0.1  # Localhost for Flask
export PORT=20001
export FLASK_DEBUG=1

echo "📍 Configuration:"
echo "   - Environment: development"
echo "   - SSL/HTTPS: enabled"
echo "   - Host: $HOST (localhost)"
echo "   - Port: $PORT"
echo "   - Ngrok: will create public HTTPS tunnel"
echo ""

# Kill any existing Flask processes on this port
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

# Start Flask development server in background
echo "🌟 Starting Flask development server..."
python -m flask run --host=$HOST --port=$PORT --cert=certs/global-cert.pem --key=certs/global-key.pem &
FLASK_PID=$!

# Wait for Flask to start
sleep 5

# Test if Flask is working locally
echo "🧪 Testing Flask server..."
if curl -k -s https://localhost:$PORT/system/health > /dev/null; then
    echo "✅ Flask server is running successfully"
else
    echo "❌ Flask server failed to start"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

# Start ngrok tunnel for HTTPS
echo "🌐 Starting ngrok HTTPS tunnel..."
ngrok http https://localhost:$PORT --log=stdout &
NGROK_PID=$!

# Wait for ngrok to start and get URL
sleep 8
NGROK_URL=$(curl -s localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data['tunnels'] else 'Not ready')" 2>/dev/null || echo "Not ready")

echo ""
echo "🎉 Development environment ready!"
echo "================================"
echo "   Flask Server: https://localhost:$PORT"
echo "   Public URL: $NGROK_URL"
echo ""
echo "📱 For mobile development, use:"
echo "   API_BASE_URL = '$NGROK_URL'"
echo ""
echo "🧪 Test endpoints:"
echo "   curl $NGROK_URL/system/health"
echo "   curl $NGROK_URL/api/status"
echo ""
echo "Press Ctrl+C to stop both servers"

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $FLASK_PID 2>/dev/null || true
    kill $NGROK_PID 2>/dev/null || true
    pkill -f "flask run" 2>/dev/null || true
    pkill -f "ngrok" 2>/dev/null || true
    echo "✅ Cleanup complete"
}

trap cleanup EXIT

# Wait for user to stop
wait 