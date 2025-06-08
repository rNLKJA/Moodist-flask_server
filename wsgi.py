"""WSGI entry point for production deployment."""

from src import create_app

# Create the application with production config
app = create_app('production')

if __name__ == "__main__":
    app.run() 