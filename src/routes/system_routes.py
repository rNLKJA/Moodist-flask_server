"""System routes for health checks and internal functionality."""

import socket
import os
from flask import jsonify, current_app, request
from src.routes import system
from datetime import datetime

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

@system.route('/health')
def health():
    """Health check endpoint for monitoring and discovery."""
    host = current_app.config.get('HOST', '127.0.0.1')
    port = current_app.config.get('PORT', 20001)
    ssl_enabled = current_app.config.get('SSL_ENABLED', False)
    
    # Determine accessibility
    if host == '0.0.0.0':
        access_type = "network-accessible"
        local_ip = get_local_ip()
        protocol = "https" if ssl_enabled else "http"
        external_url = f"{protocol}://{local_ip}:{port}"
    else:
        access_type = "localhost-only"
        external_url = None
    
    response_data = {
        "status": "ok",
        "service": current_app.config.get('APP_NAME', 'Moodist'),
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "host": {
            "bind_address": host,
            "port": port,
            "local_ip": get_local_ip() if host == '0.0.0.0' else "127.0.0.1"
        },
        "ssl": {
            "enabled": ssl_enabled,
            "protocol": "https" if ssl_enabled else "http"
        },
        "access": {
            "type": access_type,
            "external_url": external_url
        },
        "environment": os.environ.get('FLASK_CONFIG', 'development'),
        "mobile_friendly": not ssl_enabled and host == '0.0.0.0'
    }
    
    return jsonify(response_data)

@system.route('/info')
def info():
    """Provides detailed information about the application."""
    host = current_app.config.get('HOST', '127.0.0.1')
    port = current_app.config.get('PORT', 20001)
    ssl_enabled = current_app.config.get('SSL_ENABLED', False)
    protocol = "https" if ssl_enabled else "http"
    
    # Create endpoint URLs
    if host == '0.0.0.0':
        local_ip = get_local_ip()
        base_url = f"{protocol}://{local_ip}:{port}"
    else:
        base_url = f"{protocol}://localhost:{port}"
    
    return jsonify({
        "name": current_app.config.get('APP_NAME', 'Moodist'),
        "description": current_app.config.get('APP_DESCRIPTION', 'A mood tracking application'),
        "creator": "rNLKJA",
        "organization": "The University of Melbourne",
        "year": "2025",
        "server": {
            "protocol": protocol,
            "host": host,
            "port": port,
            "ssl_enabled": ssl_enabled,
            "base_url": base_url
        },
        "endpoints": {
            "main": f"{base_url}/",
            "api_status": f"{base_url}/api/status",
            "api_info": f"{base_url}/api/info",
            "health": f"{base_url}/system/health",
            "info": f"{base_url}/system/info"
        },
        "mobile_development": {
            "supported": not ssl_enabled and host == '0.0.0.0',
            "instructions": "Use HTTP URLs for Expo/React Native apps" if not ssl_enabled else "Consider disabling SSL for mobile development"
        },
        "cors": {
            "enabled": True,
            "origins": current_app.config.get('CORS_ORIGINS', ['*'])
        }
    }) 