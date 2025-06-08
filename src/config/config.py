import os

class Config:
    """Base configuration."""
    # Application
    APP_NAME = "Moodist"
    APP_DESCRIPTION = "A mood tracking application for psychiatry studies"
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    TESTING = False
    
    # SSL/TLS - Use trusted certificates by default
    SSL_ENABLED = True
    SSL_REDIRECT = False
    SSL_CERT = os.path.join(os.getcwd(), 'certs/trusted-cert.pem')
    SSL_KEY = os.path.join(os.getcwd(), 'certs/trusted-key.pem')
    
    # Network
    HOST = os.environ.get('HOST', '0.0.0.0')  # Network accessible by default
    PORT = int(os.environ.get('PORT', 20001))
    
    # CORS settings - permissive for development
    CORS_ORIGINS = ['*']
    CORS_ALLOW_HEADERS = ['*']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
    CORS_SUPPORTS_CREDENTIALS = True

class DevelopmentConfig(Config):
    """Development configuration with trusted HTTPS."""
    DEBUG = True
    SSL_ENABLED = os.environ.get('SSL_ENABLED', 'True').lower() in ('true', '1', 't')

class MobileHTTPSConfig(Config):
    """Mobile HTTPS development configuration - uses trusted certificates."""
    DEBUG = True
    SSL_ENABLED = True
    PORT = int(os.environ.get('PORT', 20443))  # Different port for mobile HTTPS

class GlobalHTTPSConfig(Config):
    """Global HTTPS configuration - uses globally trusted certificates."""
    DEBUG = True
    SSL_ENABLED = True
    PORT = int(os.environ.get('PORT', 443))  # Standard HTTPS port
    
    # Use global certificates by default
    SSL_CERT = os.environ.get('SSL_CERT', os.path.join(os.getcwd(), 'certs/global-cert.pem'))
    SSL_KEY = os.environ.get('SSL_KEY', os.path.join(os.getcwd(), 'certs/global-key.pem'))
    
    # More restrictive CORS for global deployment
    cors_origins = os.environ.get('CORS_ALLOW_ORIGINS', '')
    CORS_ORIGINS = cors_origins.split(',') if cors_origins else ['*']

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SSL_ENABLED = False  # Disable SSL for testing

class ProductionConfig(Config):
    """Production configuration."""
    # Essential production settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")
    
    # Network settings
    PORT = int(os.environ.get('PORT', 8000))
    
    # Security settings
    SSL_ENABLED = True
    SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = True
    
    # SSL/TLS settings - can override with environment variables
    # Check for global certificates first, fall back to trusted certificates
    if os.path.exists(os.path.join(os.getcwd(), 'certs/global-cert.pem')):
        SSL_CERT = os.environ.get('SSL_CERT', os.path.join(os.getcwd(), 'certs/global-cert.pem'))
        SSL_KEY = os.environ.get('SSL_KEY', os.path.join(os.getcwd(), 'certs/global-key.pem'))
    else:
        SSL_CERT = os.environ.get('SSL_CERT', os.path.join(os.getcwd(), 'certs/trusted-cert.pem'))
        SSL_KEY = os.environ.get('SSL_KEY', os.path.join(os.getcwd(), 'certs/trusted-key.pem'))
    
    # Restrict CORS in production
    cors_origins = os.environ.get('CORS_ALLOW_ORIGINS', '')
    CORS_ORIGINS = cors_origins.split(',') if cors_origins else ['*']
    
    # Log level
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Server name
    SERVER_NAME = os.environ.get('SERVER_NAME')
    
    # Proxy settings
    PREFERRED_URL_SCHEME = 'https'
    PROXY_FIX = True
    PROXY_FIX_X_FOR = 1
    PROXY_FIX_X_PROTO = 1
    PROXY_FIX_X_HOST = 1
    PROXY_FIX_X_PORT = 1

config = {
    'development': DevelopmentConfig,
    'mobile-https': MobileHTTPSConfig,
    'global-https': GlobalHTTPSConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 