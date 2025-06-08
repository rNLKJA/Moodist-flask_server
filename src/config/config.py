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
    
    # SSL/TLS
    SSL_ENABLED = True
    SSL_REDIRECT = False
    
    # Add other common configuration here

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # SSL certificate paths - using proper certificates
    SSL_CERT = os.path.join(os.getcwd(), 'certs/cert.pem')
    SSL_KEY = os.path.join(os.getcwd(), 'certs/key.pem')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ALLOW_ORIGINS', '*').split(',')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Use ephemeral certificates for testing
    SSL_CERT = None
    SSL_KEY = None
    SSL_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    # Production settings should be set via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SSL_REDIRECT = True
    
    # In production, certificates should be managed by the hosting environment
    # or a reverse proxy like Nginx/Apache
    SSL_CERT = os.environ.get('SSL_CERT')
    SSL_KEY = os.environ.get('SSL_KEY')
    SSL_ENABLED = os.environ.get('SSL_ENABLED', 'True').lower() in ('true', '1', 't')
    
    # Restrict CORS in production
    CORS_ORIGINS = os.environ.get('CORS_ALLOW_ORIGINS', '').split(',')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 