# Moodist - Mood Tracking API

A secure Flask-based API for mood tracking designed for psychiatry studies at The University of Melbourne. Built by rNLKJA with ngrok integration for seamless mobile development.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- macOS/Linux (Windows users: adapt commands as needed)

### 1. Setup

```bash
# Clone and navigate to project
git clone <repository-url>
cd flask_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp env.example .env
# Edit .env if needed (defaults work for development)
```

### 2. Start Development Server

```bash
# One command starts everything: Flask + Ngrok
./scripts/start_dev.sh
```

**This automatically:**
- ✅ Installs mkcert and generates SSL certificates
- ✅ Installs and configures ngrok (requires one-time signup)
- ✅ Starts Flask server on localhost:20001
- ✅ Creates public ngrok tunnel for mobile access
- ✅ Displays your public URL

**First-time setup**: You'll need to:
1. Sign up at [ngrok.com](https://ngrok.com/signup) (free)
2. Get your authtoken from [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
3. Run: `ngrok config add-authtoken YOUR_TOKEN`

### 3. Development Ready! 🎉

After running `./scripts/start_dev.sh`, you'll see:

```
🎉 Development environment ready!
================================
   Flask Server: https://localhost:20001
   Public URL: https://abc123.ngrok.io

📱 For mobile development, use:
   API_BASE_URL = 'https://abc123.ngrok.io'
```

## 📱 Mobile App Integration

### React Native / Expo
```javascript
// Use the ngrok URL from your terminal output
const API_BASE_URL = 'https://abc123.ngrok.io';

// Test connection
const testAPI = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/system/health`);
    const data = await response.json();
    console.log('API Status:', data.status); // Should show "ok"
  } catch (error) {
    console.error('API Error:', error);
  }
};

// Your mood tracking API calls
const getMoodData = async () => {
  const response = await fetch(`${API_BASE_URL}/api/status`);
  return response.json();
};
```

### Benefits
- ✅ **Globally trusted SSL** - No certificate warnings
- ✅ **Works on any device** - No network configuration needed
- ✅ **Real HTTPS** - Production-like environment
- ✅ **Team sharing** - Send ngrok URL to teammates

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/system/health` | GET | Health check |
| `/system/info` | GET | System information |
| `/api/status` | GET | API status |
| `/` | GET | Welcome page |

### Test with curl
```bash
# Replace with your ngrok URL
curl https://abc123.ngrok.io/system/health
curl https://abc123.ngrok.io/api/status
```

## 🛠️ Development Workflow

### Daily Development
```bash
# Start development (one command)
./scripts/start_dev.sh

# Copy the ngrok URL shown in terminal
# Use it in your mobile app as API_BASE_URL

# Stop with Ctrl+C (cleans up automatically)
```

### Production Deployment
```bash
# For production, use global certificates
./scripts/setup_letsencrypt.sh yourdomain.com your-email@example.com

# Start production server
./scripts/start_production.sh
```

## 📁 Project Structure

```
flask_server/
├── src/                     # Application source
│   ├── config/              # Configuration settings
│   ├── controllers/         # Business logic
│   ├── middleware/          # Request processing
│   ├── models/              # Data models
│   ├── routes/              # API routes
│   └── utils/               # Utilities
├── scripts/                 # Development scripts
│   ├── start_dev.sh         # Main development script
│   ├── setup_letsencrypt.sh # Production SSL setup
│   └── start_production.sh  # Production server
├── certs/                   # SSL certificates
├── .env                     # Environment configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔒 Security Features

- **HTTPS Everywhere**: All connections use SSL/TLS encryption
- **CORS Protection**: Configurable cross-origin request handling  
- **Request Logging**: Comprehensive request/response logging
- **Error Handling**: Graceful error responses
- **Input Validation**: Request validation middleware

## 🐛 Troubleshooting

### "Ngrok not authenticated"
```bash
# Sign up at ngrok.com and get your authtoken
ngrok config add-authtoken YOUR_TOKEN
```

### "Port already in use"
```bash
# Kill any running Flask processes
pkill -f "flask run"
./scripts/start_dev.sh
```

### "mkcert not found"
```bash
# macOS
brew install mkcert

# Linux
sudo apt install libnss3-tools
wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert && sudo mv mkcert /usr/local/bin/
```

### Mobile app can't connect
- ✅ Use the **ngrok URL** (not localhost)
- ✅ Ensure ngrok tunnel is running
- ✅ Check your mobile device has internet access

## 🎯 Why Ngrok?

**Traditional local development problems:**
- ❌ Mobile devices can't access localhost
- ❌ SSL certificate warnings on mobile
- ❌ Network configuration headaches
- ❌ Different URLs for different environments

**Ngrok solves all of this:**
- ✅ **Instant global access** - Works from anywhere
- ✅ **Trusted SSL certificates** - No warnings
- ✅ **One URL** - Same for all devices
- ✅ **Team collaboration** - Share with anyone

## 🔗 Useful Links

- **Ngrok**: https://ngrok.com
- **mkcert**: https://github.com/FiloSottile/mkcert
- **Flask**: https://flask.palletsprojects.com
- **University of Melbourne**: https://www.unimelb.edu.au

---

**Built with ❤️ by rNLKJA for The University of Melbourne Psychiatry Department** 