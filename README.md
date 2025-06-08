# Moodist - Track Your Mood, Improve Your Mental Health

A secure Flask-based API for mood tracking designed for psychiatry studies. Built by rNLKJA with proper HTTPS support and an Express.js-like organization.

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd flask_server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
```bash
# Create a .env file based on the env_example.txt
cp env_example.txt .env
# Edit the .env file with your specific settings
```

## SSL Certificates

For development, self-signed certificates are generated in the `certs` directory:
- `certs/cert.pem`: SSL Certificate
- `certs/key.pem`: SSL Private Key

If you need to regenerate the certificates:
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365 -subj "/CN=localhost"
```

> **Note**: Self-signed certificates will trigger browser warnings. This is normal for development.

## Running the Server

Run the server with:
```bash
python run.py
```

The server will start in development mode with HTTPS support by default.

Access the server at:
- HTTPS: https://localhost:5001/
- API Status: https://localhost:5001/api/status
- API Info: https://localhost:5001/api/info

## Configuration

You can change the server configuration by setting the `FLASK_CONFIG` environment variable:
- `development` (default): Debug mode with HTTPS support
- `testing`: For running tests
- `production`: For production deployment (without HTTPS, use a reverse proxy)

Example:
```bash
FLASK_CONFIG=production python run.py
```

## Project Structure

```
flask_server/
├── certs/                   # SSL certificates
├── src/                     # Application source code
│   ├── config/              # Configuration settings
│   ├── controllers/         # Business logic handlers
│   ├── middleware/          # Request processing middleware
│   ├── models/              # Data models
│   ├── routes/              # Route definitions
│   └── utils/               # Utility functions
├── static/                  # Static files
├── templates/               # Template files
├── app.py                   # Application entry point
├── run.py                   # Script to run the server
├── requirements.txt         # Project dependencies
├── env_example.txt          # Example environment variables
├── CHANGELOG.md             # Record of project changes
└── README.md                # Project documentation
```

## Express.js-like Organization

This project follows principles from Express.js organization:

- **Routes**: Define endpoints and HTTP methods
- **Controllers**: Handle business logic
- **Middleware**: Process requests before/after controllers
- **Models**: Define data structures
- **Config**: Application configuration
- **Utils**: Shared utility functions 