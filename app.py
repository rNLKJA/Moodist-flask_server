"""Main application entry point."""

import os
from src import create_app

if __name__ == '__main__':
    # Get config from environment or default to development
    app_config = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(app_config)
    
    # Get port from environment or default to 5001
    port = int(os.environ.get('PORT', 5001))
    
    # Configure SSL context if enabled
    ssl_context = None
    if app.config.get('SSL_ENABLED', False) and app.config.get('SSL_CERT') and app.config.get('SSL_KEY'):
        ssl_context = (app.config['SSL_CERT'], app.config['SSL_KEY'])
        print(f"Starting {app.config.get('APP_NAME')} in {app_config.upper()} mode with HTTPS support...")
    else:
        print(f"Starting {app.config.get('APP_NAME')} in {app_config.upper()} mode without HTTPS...")
    
    # Run the application
    app.run(
        host='0.0.0.0', 
        port=port,
        ssl_context=ssl_context,
        debug=app.config['DEBUG']
    ) 