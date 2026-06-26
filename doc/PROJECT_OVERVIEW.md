# 🎯 Moodist Flask Server - Project Overview

> **A mood tracking application for psychiatry studies at The University of Melbourne**
>
> Created by rNLKJA | Current Version: 1.5.0

## 🚀 **Key Features & Capabilities**

### 🌐 **Instant Global Development**

- **One-command setup**: `./scripts/start_dev.sh` handles everything
- **Ngrok integration**: Get globally accessible HTTPS URLs instantly
- **Mobile-ready**: No certificate installation needed on devices
- **Team collaboration**: Share ngrok URLs for immediate testing

### 🔒 **Production-Grade Security**

- **HTTPS everywhere**: Trusted certificates for all environments
- **Mobile compatible**: Works with Android API 28+ and iOS ATS
- **SSL/TLS encryption**: Proper security for production deployment
- **Environment-based config**: Development, staging, and production settings

### 📱 **Mobile Development Excellence**

- **Global HTTPS access**: Test from anywhere in the world
- **Real-time tunneling**: Automatic ngrok URL generation
- **Cross-platform ready**: iOS and Android compatibility
- **Zero configuration**: Mobile devices work immediately

### 🏗️ **Modern Architecture**

- **Flask application factory**: Scalable and maintainable structure
- **Blueprint organization**: Modular route and controller system
- **Middleware pipeline**: Request processing and logging
- **MVC-like structure**: Clear separation of concerns

## 📋 **Quick Start**

### Development Environment

```bash
# Clone and setup
git clone <repository>
cd flask_server

# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start development server (includes ngrok)
./scripts/start_dev.sh
```

### Production Deployment

```bash
# Setup SSL certificates (one-time)
./scripts/setup_letsencrypt.sh yourdomain.com

# Start production server
./scripts/start_production.sh
```

## 🔧 **Development Workflow**

### Current Architecture (v1.5.0)

```
├── 🎯 Single Command Development
│   └── ./scripts/start_dev.sh (auto-generates certificates + ngrok)
├── 🌍 Global HTTPS Access
│   └── Ngrok tunnel with trusted certificates
├── 📱 Mobile Development
│   └── Copy-paste ngrok URL for immediate testing
└── 🚀 Production Ready
    └── Let's Encrypt + Gunicorn configuration
```

### What Happens When You Run `start_dev.sh`:

1. ✅ **Certificate Check**: Auto-generates mkcert certificates if needed
2. ✅ **Ngrok Setup**: Installs and authenticates ngrok automatically
3. ✅ **Flask Server**: Starts HTTPS server on `https://localhost:20001`
4. ✅ **Global Tunnel**: Creates ngrok HTTPS tunnel
5. ✅ **URL Display**: Shows public URL for mobile development
6. ✅ **Health Check**: Validates server before tunnel creation

## 📊 **Project Evolution**

### Major Milestones (Referenced from [CHANGELOG.md](./CHANGELOG.md))

#### **v1.5.0 - Ngrok Integration Revolution** 🚀

- **70% script reduction**: From 12+ scripts to 3 essential ones
- **One-command development**: Complete environment setup
- **Global HTTPS access**: Instant worldwide connectivity
- **Mobile development overhaul**: Zero-configuration mobile testing

#### **v1.4.0 - Certificate Simplification** 🔒

- **Trusted certificates only**: Eliminated self-signed certificates
- **Mobile compatibility**: Android API 28+ and iOS ATS compliant
- **Security enhancement**: Removed SSL verification bypasses

#### **v1.3.0 - Mobile Development Enhancement** 📱

- **Mobile HTTPS mode**: Locally-trusted certificates with mkcert
- **Network accessibility**: Proper mobile device connectivity
- **Certificate analysis**: Tools for troubleshooting SSL issues

#### **v1.2.0 - Production Deployment** 🏭

- **Gunicorn integration**: WSGI server for production
- **Security hardening**: CSRF protection, secure sessions
- **SSL/TLS production**: Let's Encrypt certificate support

## 🎯 **Current Capabilities**

### API Endpoints

- **Health Check**: `/system/health` - Application status and diagnostics
- **System Info**: `/system/info` - Server environment details
- **API Status**: `/api/status` - API service status
- **API Info**: `/api/info` - API version and capabilities

### Development Features

- **Auto-reload**: Flask development server with hot reload
- **Debug mode**: Comprehensive error reporting
- **Logging**: Structured logging with configurable levels
- **CORS**: Permissive CORS for cross-origin development

### Production Features

- **Gunicorn WSGI**: Production-grade application server
- **SSL termination**: HTTPS with Let's Encrypt certificates
- **Process management**: Multi-worker configuration
- **Security headers**: HSTS, CSP, and security hardening

## 🛠️ **Technical Stack**

### Core Technologies

- **Backend**: Flask (Python web framework)
- **WSGI Server**: Gunicorn (production)
- **SSL/TLS**: mkcert (development) + Let's Encrypt (production)
- **Tunneling**: Ngrok (global access)

### Development Tools

- **Certificate Management**: mkcert for trusted local certificates
- **Global Access**: Ngrok for instant HTTPS tunneling
- **Environment Management**: Python virtual environments
- **Configuration**: Environment-based settings

### Security Implementation

- **HTTPS Everywhere**: No HTTP endpoints in any environment
- **Trusted Certificates**: Browser and mobile device compatibility
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **CORS Configuration**: Environment-appropriate CORS settings

## 📁 **Project Structure**

```
flask_server/
├── 📄 PROJECT_OVERVIEW.md     # This overview document
├── 📄 CHANGELOG.md            # Detailed version history
├── 📄 README.md               # Technical setup guide
├── 📁 scripts/                # Essential automation scripts
│   ├── start_dev.sh          # 🎯 One-command development
│   ├── setup_letsencrypt.sh  # Production SSL setup
│   └── start_production.sh   # Production server startup
├── 📁 src/                    # Application source code
│   ├── routes/               # URL routing and endpoints
│   ├── controllers/          # Business logic
│   ├── middleware/           # Request processing
│   ├── models/               # Data models
│   ├── utils/                # Helper functions
│   └── config/               # Configuration management
├── 📁 api/                    # API-specific code
│   ├── routes/               # API endpoints
│   ├── models/               # API data models
│   └── services/             # API business logic
├── 📁 logs/                   # Application logs
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env                    # Environment configuration
└── 📄 wsgi.py                 # Production WSGI entry point
```

## 🎯 **Next Steps & Roadmap**

### Immediate Benefits Available

- ✅ **Start developing immediately**: Run `./scripts/start_dev.sh`
- ✅ **Test on mobile devices**: Use ngrok URL as API_BASE_URL
- ✅ **Share with team**: Send ngrok URL for collaboration
- ✅ **Deploy to production**: Use `./scripts/setup_letsencrypt.sh`

### Development Workflow

1. **Local Development**: `./scripts/start_dev.sh` for complete environment
2. **Mobile Testing**: Copy ngrok URL to mobile app configuration
3. **Team Collaboration**: Share ngrok URL for immediate access
4. **Production Deployment**: Use Let's Encrypt for production SSL

## 📞 **Support & Documentation**

- **Setup Guide**: See [README.md](./README.md) for technical setup
- **Change History**: See [CHANGELOG.md](./CHANGELOG.md) for detailed version history
- **Scripts Documentation**: All scripts include help text with `--help` flag

---

**Created by rNLKJA for The University of Melbourne Psychiatry Department**

_This project represents a comprehensive Flask server solution optimized for mobile app development with instant global accessibility and production-ready deployment capabilities._
