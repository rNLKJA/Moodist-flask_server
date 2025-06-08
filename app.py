"""Main application entry point."""

import os
from src import create_app

if __name__ == '__main__':
    # Get config from environment or default to development
    app_config = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(app_config)
    
    # Get host and port from app configuration
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', 20001)
    
    # Configure SSL context if enabled
    ssl_context = None
    if app.config.get('SSL_ENABLED', False) and app.config.get('SSL_CERT') and app.config.get('SSL_KEY'):
        ssl_context = (app.config['SSL_CERT'], app.config['SSL_KEY'])
        protocol = "HTTPS"
    else:
        protocol = "HTTP"
    
    print(f"Starting {app.config.get('APP_NAME')} in {app_config.upper()} mode...")
    print(f"Server: {protocol}://{host}:{port}")
    print(f"SSL Enabled: {app.config.get('SSL_ENABLED', False)}")
    print(f"Debug Mode: {app.config.get('DEBUG', False)}")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        ssl_context=ssl_context,
        debug=app.config['DEBUG']
    ) 