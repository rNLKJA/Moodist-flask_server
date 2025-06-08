import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    TESTING = False
    # Add other common configuration here

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SSL_CERT = os.path.join(os.getcwd(), 'certs/cert.pem')
    SSL_KEY = os.path.join(os.getcwd(), 'certs/key.pem')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    # Production settings should be set via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # Production may use real certificates from a provider

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 