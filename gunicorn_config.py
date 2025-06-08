"""Gunicorn configuration file."""

import os
import multiprocessing

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')  # Default to network accessible
backlog = 2048

# Worker processes
workers = os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
pidfile = 'gunicorn.pid'
umask = 0
user = None
group = None

# Logging
errorlog = 'logs/gunicorn-error.log'
accesslog = 'logs/gunicorn-access.log'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'moodist'

# SSL/TLS configuration - using trusted certificates
certfile = os.environ.get('SSL_CERT', 'certs/trusted-cert.pem')
keyfile = os.environ.get('SSL_KEY', 'certs/trusted-key.pem')
ssl_version = 'TLSv1_2'
do_handshake_on_connect = True

# Server hooks
def on_starting(server):
    """Server startup actions."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    print(f"Starting Gunicorn server with {workers} workers on {bind}")
    print(f"Network accessible: {'Yes' if '0.0.0.0' in bind else 'Limited'}")
    print(f"Using trusted certificates: {certfile}")

def on_exit(server):
    """Server shutdown actions."""
    print("Gunicorn server shutting down") 