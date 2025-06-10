# Changelog

All notable changes to this project will be documented in this file.

## [1.7.0] - 2024-12-10 - Session Management & User Authentication

### 🔐 **Session Management System**
- **NEW**: Secure session management with Flask-Session and Flask-Login
- **ADDED**: Login, logout, and session status endpoints
- **ENHANCED**: Cross-database user authentication
- **IMPROVED**: Session security with HTTPS-only cookies and proper expiration
- **IMPLEMENTED**: Industry best practices for session handling and storage

### 👤 **User Authentication Enhancements**
- **NEW**: User model with Flask-Login integration
- **ADDED**: Login history tracking and monitoring
- **ENHANCED**: Password change functionality with secure verification
- **IMPROVED**: Cross-database user lookup by email and ID
- **SECURED**: Protection against timing attacks and brute force attempts

### 🛡️ **Security Improvements**
- **ADDED**: HttpOnly, Secure, and SameSite cookie attributes
- **ENHANCED**: Session signing and encryption
- **IMPLEMENTED**: Strong session protection mode
- **IMPROVED**: CSRF protection for authenticated routes
- **ADDED**: Automatic session expiration after 24 hours

### 🔄 **API Enhancements**
- **NEW**: RESTful authentication endpoints
- **ADDED**: Session status checking endpoint
- **ENHANCED**: User type-specific authentication
- **IMPROVED**: Consistent error handling and status codes
- **IMPLEMENTED**: Proper HTTP response codes for authentication outcomes

## [1.6.0] - 2024-12-09 - Enhanced Authentication System & Email Styling

### 🔐 **Authentication System Overhaul**
- **NEW**: 6-character uppercase document IDs for improved user reference
- **ENHANCED**: Email verification workflow with simplified success page
- **IMPROVED**: Database routing based on user type (patient/doctor/admin)
- **MODERNIZED**: Email templates with Moodist brand styling
- **ADDED**: University of Melbourne branding integration

### 📧 **Email System Improvements**
- **REDESIGNED**: Modern email template with responsive design
- **UPDATED**: Clean, professional verification success page
- **ENHANCED**: Email styling to match mobile app aesthetic
- **IMPROVED**: Plain text fallback for email clients without HTML support
- **ADDED**: University of Melbourne logo integration

### 🔄 **CouchDB Integration**
- **OPTIMIZED**: User document structure with type-specific database routing
- **ENHANCED**: Unique ID generation with multi-database collision detection
- **IMPROVED**: Document updating with proper revision handling
- **ADDED**: Smart duplicate user handling with verification resending

### 🔒 **Security Enhancements**
- **UPGRADED**: Password hashing with Argon2id (industry best practice)
- **ENHANCED**: Token expiration and validation
- **IMPROVED**: Error handling and logging throughout authentication flow
- **ADDED**: Comprehensive validation of user inputs

### 🎨 **UI/UX Improvements**
- **MODERNIZED**: User interfaces with consistent branding
- **SIMPLIFIED**: Verification success messages for better user experience
- **ENHANCED**: Email templates with gradient backgrounds matching app
- **IMPROVED**: Responsive design for all screen sizes

### 🧰 **Developer Experience**
- **ENHANCED**: Code organization with better function documentation
- **IMPROVED**: Error handling with detailed logging
- **ADDED**: Type hints and docstrings for better code readability
- **SIMPLIFIED**: User lookup and database routing

## [1.5.0] - 2024-12-08 - Ngrok Integration & Development Environment Optimization

### 🚀 **Major Development Environment Overhaul**
- **NEW**: Automated ngrok integration for instant global HTTPS access
- **NEW**: Single-command development startup (`./scripts/start_dev.sh`)
- **NEW**: Automatic certificate generation and ngrok tunnel creation
- **SIMPLIFIED**: Removed 9+ unnecessary scripts and consolidated functionality
- **ENHANCED**: Real-time Flask + ngrok coordination with proper HTTPS tunneling

### 🔧 **Fixed Critical Issues**
- **FIXED**: Logger middleware `AttributeError: start_time` causing 500 errors
- **FIXED**: Ngrok HTTP/HTTPS mismatch preventing proper tunneling
- **FIXED**: .env file parsing errors with inline comments
- **IMPROVED**: Error handling and graceful cleanup on script termination

### 🌐 **Ngrok Integration Features**
- **AUTOMATIC**: Certificate generation with mkcert if not present
- **AUTOMATIC**: Ngrok installation and authentication check
- **AUTOMATIC**: HTTPS tunnel creation pointing to Flask server
- **REAL-TIME**: Public URL display for immediate mobile development
- **VALIDATION**: Flask server health check before ngrok tunnel creation

### 📱 **Mobile Development Improvements**
- **INSTANT**: Globally accessible HTTPS URLs for mobile apps
- **TRUSTED**: SSL certificates accepted by all devices worldwide
- **SEAMLESS**: No mobile device certificate installation required
- **PRODUCTION-LIKE**: Real HTTPS environment for accurate testing

### 🧹 **Code Cleanup & Simplification**
- **REMOVED**: 9 unnecessary scripts (all certificate variants, multiple startup options)
- **SIMPLIFIED**: Single development workflow with ngrok
- **STREAMLINED**: Clean project structure with essential scripts only
- **UPDATED**: README with clear ngrok-focused development guide

### 📋 **Scripts Removed**
- `scripts/check_certificate.sh` - Certificate analysis (no longer needed)
- `scripts/setup_global_certs.sh` - Manual certificate setup
- `scripts/setup_mobile_ca.sh` - Mobile CA installation
- `scripts/setup_ngrok.sh` - Standalone ngrok setup
- `scripts/start_dev_global.sh` - Global certificate variant
- `scripts/start_dev_http.sh` - HTTP-only variant
- `scripts/start_mobile_https.sh` - Mobile-specific variant
- `scripts/start_global_https.sh` - Global HTTPS variant
- `scripts/verify_cert.sh` - Certificate verification

### 📋 **Scripts Maintained**
- `scripts/start_dev.sh` - **🆕 ENHANCED**: All-in-one development environment
- `scripts/setup_letsencrypt.sh` - Production SSL certificate setup
- `scripts/start_production.sh` - Production server startup

### 🔄 **Development Workflow Changes**
- **BEFORE**: Multiple scripts for different certificate types and environments
- **AFTER**: Single command (`./scripts/start_dev.sh`) for complete development setup
- **BEFORE**: Manual ngrok tunnel creation and URL management
- **AFTER**: Automatic ngrok integration with real-time URL display
- **BEFORE**: Local network access with certificate warnings
- **AFTER**: Global HTTPS access with trusted certificates

### 📱 **Mobile Integration Enhancements**
- **SIMPLIFIED**: No certificate installation on mobile devices
- **GLOBAL**: Works from anywhere in the world
- **INSTANT**: Copy-paste ngrok URL for immediate mobile development
- **RELIABLE**: Proper HTTPS tunneling eliminates connection issues

### 🐛 **Bug Fixes**
- **FIXED**: `start_time` AttributeError in logger middleware
- **FIXED**: Ngrok tunneling to HTTP while Flask serves HTTPS
- **FIXED**: Environment variable parsing with inline comments
- **FIXED**: Port conflicts and process cleanup issues

### 🎯 **Performance & Reliability**
- **IMPROVED**: Faster development startup with health checks
- **ENHANCED**: Proper process management and cleanup
- **ADDED**: Automatic Flask server validation before ngrok tunnel
- **OPTIMIZED**: Single point of failure elimination

### 📚 **Documentation Updates**
- **REWRITTEN**: README.md with ngrok-focused development guide
- **SIMPLIFIED**: Environment configuration examples
- **ADDED**: Mobile app integration examples with ngrok URLs
- **ENHANCED**: Troubleshooting section for common ngrok issues

### 🔒 **Security Improvements**
- **MAINTAINED**: HTTPS-only development environment
- **ENHANCED**: Proper SSL certificate handling
- **SIMPLIFIED**: Reduced attack surface by removing unused scripts
- **SECURED**: Environment variable handling improvements

### 💡 **Key Benefits Delivered**
- ✅ **One-command development** - `./scripts/start_dev.sh` does everything
- ✅ **Global HTTPS access** - No network configuration needed
- ✅ **Mobile-ready immediately** - Copy ngrok URL and start developing
- ✅ **Production-like environment** - Real HTTPS with trusted certificates
- ✅ **Team collaboration** - Share ngrok URL with team members instantly
- ✅ **Simplified maintenance** - 70% fewer scripts to maintain

### 🚨 **Breaking Changes**
- **REMOVED**: All certificate variant scripts (use `start_dev.sh` instead)
- **CHANGED**: Development workflow now requires ngrok account (free)
- **SIMPLIFIED**: No more multiple startup options - single script handles all cases
- **REQUIRED**: Ngrok authentication token needed for development

### 🎯 **Migration Guide**
```bash
# OLD: Multiple scripts for different scenarios
./scripts/start_mobile_https.sh
./scripts/start_dev_global.sh
./scripts/start_mobile_dev.sh

# NEW: Single script for all development needs
./scripts/start_dev.sh
```

## [1.4.0] - 2024-12-08 - Certificate Simplification

### Security & Certificates
- **SIMPLIFIED**: Removed all self-signed certificates and scripts
- **TRUSTED ONLY**: Now uses only mkcert-generated trusted certificates
- **MOBILE COMPATIBLE**: All modes now use HTTPS with trusted certificates
- **SECURITY**: Eliminated SSL verification bypasses and certificate warnings

### Configuration Updates
- **Streamlined**: Removed `mobile` HTTP configuration mode
- **Unified**: All environments now use trusted certificates by default
- **Network Access**: All modes are network accessible (0.0.0.0) by default
- **Port Consistency**: Development (20001), Mobile HTTPS (20443), Production (8000)

### Scripts & Documentation
- **Removed**: `scripts/generate_certs.sh` (self-signed certificate generation)
- **Removed**: `scripts/start_mobile_dev.sh` (HTTP mobile mode)
- **Updated**: All scripts now reference trusted certificates only
- **Simplified**: `scripts/verify_cert.sh` now works with trusted certificates only
- **Enhanced**: README completely rewritten for trusted certificate approach

### Breaking Changes
- ⚠️ **HTTP Mode Removed**: No longer supports HTTP development mode
- ⚠️ **Self-signed Certificates**: Removed support for self-signed certificates
- ⚠️ **Mobile Setup Required**: Mobile devices must install CA certificate (one-time)

### Benefits
- ✅ **No Browser Warnings**: Trusted certificates work without bypasses
- ✅ **Mobile Production Ready**: Works with Android API 28+ and iOS ATS
- ✅ **Simplified Setup**: One certificate type for all environments
- ✅ **Better Security**: Proper SSL/TLS encryption everywhere

## [1.3.0] - 2024-12-08 - Mobile Development Enhancement

### Mobile Development
- **NEW**: Mobile HTTPS mode with locally-trusted certificates (mkcert)
- **NEW**: Certificate analysis script to identify certificate types
- **IMPROVED**: Mobile device CA certificate setup with detailed instructions
- **ENHANCED**: Network accessibility reporting in system info endpoint

### SSL/HTTPS Improvements
- **ADDED**: Support for locally-trusted certificates using mkcert
- **IMPROVED**: Certificate verification and troubleshooting
- **ENHANCED**: SSL configuration with better mobile compatibility
- **FIXED**: Certificate path handling across different environments

### Scripts & Automation
- **NEW**: `scripts/setup_mobile_ca.sh` - Mobile CA certificate installation
- **NEW**: `scripts/check_certificate.sh` - Certificate type analysis
- **IMPROVED**: Certificate generation with better error handling
- **ENHANCED**: Mobile HTTPS startup script with IP detection

### Documentation
- **EXPANDED**: Mobile development guide with iOS/Android instructions
- **ADDED**: Certificate troubleshooting section
- **IMPROVED**: Setup instructions for different operating systems
- **ENHANCED**: API endpoint documentation with mobile examples

## [1.2.0] - 2024-12-08 - Production Deployment

### Production Features
- **NEW**: Gunicorn WSGI server configuration for production
- **NEW**: Production startup script with proper SSL support
- **NEW**: Environment-specific configuration system
- **NEW**: Enhanced security settings for production deployment

### Security Enhancements
- **ADDED**: CSRF protection with WTF-CSRF
- **ADDED**: Secure session cookie configuration
- **ADDED**: SSL redirect and HSTS headers
- **ADDED**: ProxyFix middleware for reverse proxy deployment
- **IMPROVED**: Production environment validation

### Infrastructure
- **NEW**: Gunicorn configuration file with SSL support
- **NEW**: WSGI entry point for production servers
- **ADDED**: Process management and logging configuration
- **ENHANCED**: Error handling and graceful shutdown

### Documentation
- **ADDED**: Production deployment guide
- **ADDED**: Gunicorn configuration documentation
- **ENHANCED**: Environment variable documentation
- **IMPROVED**: Project structure documentation

## [1.1.0] - 2024-12-08 - Mobile Development Support

### Mobile Development
- **NEW**: Mobile development configuration mode (HTTP)
- **NEW**: Network-accessible server binding (0.0.0.0)
- **NEW**: Mobile development startup script
- **NEW**: IP address detection for mobile connection

### CORS & Network
- **ENHANCED**: Comprehensive CORS configuration for mobile apps
- **ADDED**: Permissive CORS settings for development
- **IMPROVED**: Network accessibility indicators
- **ADDED**: Local IP address reporting

### SSL/HTTPS
- **NEW**: SSL certificate generation script
- **NEW**: Certificate verification utilities
- **ADDED**: Self-signed certificate support
- **IMPROVED**: HTTPS configuration flexibility

### Documentation
- **ADDED**: Mobile development guide
- **ADDED**: Troubleshooting section for mobile connectivity
- **ENHANCED**: API endpoint documentation
- **IMPROVED**: Setup and configuration instructions

## [1.0.0] - 2024-12-08 - Initial Release

### Core Features
- **NEW**: Flask application with Express.js-like structure
- **NEW**: Application factory pattern with blueprints
- **NEW**: Configuration system for multiple environments
- **NEW**: Health check and system information endpoints

### Architecture
- **IMPLEMENTED**: MVC-like organization (routes, controllers, models)
- **ADDED**: Middleware system for request processing
- **CREATED**: Utility functions and helper modules
- **ESTABLISHED**: Project structure following best practices

### API Endpoints
- **NEW**: Health check endpoint (`/system/health`)
- **NEW**: System information endpoint (`/system/info`)
- **NEW**: API status endpoint (`/api/status`)
- **NEW**: API information endpoint (`/api/info`)

### Development Tools
- **ADDED**: Development server configuration
- **ADDED**: Environment variable management
- **CREATED**: Requirements and dependency management
- **ESTABLISHED**: Git repository structure

### Documentation
- **CREATED**: Comprehensive README with setup instructions
- **ADDED**: API documentation
- **INCLUDED**: Project structure documentation
- **ESTABLISHED**: Changelog for tracking changes

## [0.6.0] - 2024-10-23

### Added
- Enhanced SSL certificate generation for better compatibility with API clients
- Added support for PKCS#12 certificate format
- Created combined certificate and key file for clients that need it
- Added detailed Postman instructions to fix "Unable to verify the first certificate" warnings
- Updated port configuration to use 20001 consistently

## [0.5.0] - 2024-10-23

### Changed
- Disabled network accessibility by changing host from 0.0.0.0 to 127.0.0.1
- Updated system health endpoint to reflect localhost-only access
- Added HOST configuration parameter to env.example
- Updated documentation to explain access restrictions
- Enhanced security by limiting access to local machine only

## [0.4.0] - 2024-10-23

### Added
- Enhanced network accessibility for cross-application communication
- Added system endpoints for health checks and application discovery
- Added detailed host and environment information in health check response
- Created new example environment file with better documentation
- Expanded CORS settings to allow all origins for all routes
- Updated documentation with network accessibility information

## [0.3.1] - 2024-10-23

### Changed
- Updated SSL certificates to include "rNLKJA" in email addresses
- Updated verification script to validate the new certificates
- Fixed port configuration issue in the development server

## [0.3.0] - 2024-10-23

### Changed
- Renamed application to "Moodist" - A mood tracking application for psychiatry studies
- Added application creator and description
- Implemented robust SSL/TLS configuration with proper certificate generation
- Added SSL middleware for HTTP to HTTPS redirection
- Implemented security headers (HSTS, CSP, X-Content-Type-Options, X-Frame-Options)
- Added scripts for certificate generation and verification

## [0.2.1] - 2024-10-23

### Changed
- Changed default port from 5000 to 5001 to avoid conflict with macOS AirPlay Receiver

## [0.2.0] - 2024-10-23

### Changed
- Restructured project to follow Express.js-like organization
- Moved code to `src` directory with clear separation of concerns
- Implemented controller-based architecture
- Added middleware support
- Created utility functions for logging
- Improved error handling
- Added CHANGELOG.md to track project changes

## [0.1.0] - 2024-10-23

### Added
- Initial Flask server setup with virtual environment
- HTTPS support for development using self-signed certificates
- Basic API endpoints
- Configuration system for different environments
- Environment variable loading from .env file
- Documentation in README.md
- Project structure with blueprints 