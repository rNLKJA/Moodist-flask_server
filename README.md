<div align="center">

# 🧠 Moodist — Flask Server

**A secure mood-tracking API for psychiatry studies at The University of Melbourne**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![CouchDB](https://img.shields.io/badge/CouchDB-database-e42528?style=flat-square&logo=apachecouchdb&logoColor=white)](https://couchdb.apache.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-production-499848?style=flat-square&logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)

</div>

## Overview

Moodist is the backend API powering a mood-tracking application used in psychiatry research at **The University of Melbourne**. It is a **Flask** service built on the application-factory pattern, backed by **CouchDB**, with patient/clinician accounts, email-verified registration, JWT and session authentication, daily mood logging, and patient–clinician connections.

The development workflow pairs **mkcert** SSL with an **ngrok** tunnel so mobile clients can reach a trusted HTTPS endpoint instantly; production runs under **Gunicorn** with Let's Encrypt certificates.

> ⚠️ **Security note:** earlier commits in this repository's history contain a real `.env`, `.env.backup` and TLS private keys that were committed by mistake. Those secrets should be treated as compromised — rotate them (Flask `SECRET_KEY`, password salt/pepper, CouchDB and email credentials) and remove the files from history before any public or production use. The `.gitignore` now blocks these paths going forward, and [`env.example`](env.example) is the template for a fresh `.env`.

## Highlights

- **Application-factory architecture** — `create_app()` wires configuration, extensions, middleware and blueprints.
- **Role-based accounts** — patients and clinicians, with email-verified sign-up and password reset.
- **Authentication** — Flask-Login sessions, Argon2 password hashing and JWT verification links/codes.
- **Mood logging** — daily mood entries with reference lines for clinician dashboards.
- **Connections** — link patients to clinicians and exchange support messages.
- **Mobile-friendly dev loop** — one script (`scripts/start_dev.sh`) brings up Flask + mkcert SSL + ngrok.

## Tech Stack

| Layer         | Technology                                                    |
| ------------- | ------------------------------------------------------------- |
| Web framework | Flask 3.1 (application factory + blueprints)                  |
| Database      | CouchDB                                                       |
| Auth          | Flask-Login, Flask-Session, Argon2 (`argon2-cffi`), PyJWT     |
| Email         | SMTP via `email_sender` utility with HTML templates           |
| Server        | Gunicorn (production), Flask dev server + ngrok (development) |
| TLS           | mkcert (dev), Let's Encrypt (production)                      |
| Tooling       | Black, isort, python-dotenv                                   |

## Project Structure

```
flask_server/
├── app.py / run.py / wsgi.py   # Entry points (dev / run / WSGI)
├── config.py                   # Top-level config classes
├── src/
│   ├── __init__.py             # create_app() application factory
│   ├── config/                 # Environment configuration
│   ├── controllers/            # Business logic
│   ├── middleware/             # CORS, SSL, ngrok, logging, error handling
│   ├── models/                 # User, MoodLog, Verification
│   ├── routes/                 # Blueprints: auth, mood, patient, connection, system, api
│   └── utils/                  # CouchDB client, email, token & id generators
├── api/                        # Lightweight API blueprint
├── scripts/                    # start_dev.sh, start_production.sh, setup_letsencrypt.sh
├── test/                       # Standalone workflow/auth test scripts
├── doc/                        # API and setup documentation
├── requirements.txt
├── env.example                 # Environment template — copy to .env
└── _archive/                   # Previous README kept for reference
```

## Getting Started

### Prerequisites

- Python 3.8+
- A running CouchDB instance
- (Optional, for mobile testing) ngrok and mkcert

### Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your own SECRET_KEY, CouchDB and email credentials
```

### Run

```bash
# Development (Flask + mkcert SSL + ngrok tunnel)
./scripts/start_dev.sh

# Or run the app directly
python app.py

# Production (Gunicorn)
./scripts/start_production.sh
```

## Selected Endpoints

| Endpoint                            | Method              | Description                        |
| ----------------------------------- | ------------------- | ---------------------------------- |
| `/system/health`                    | GET                 | Health check                       |
| `/system/info`                      | GET                 | System information                 |
| `/api/status`                       | GET                 | API status                         |
| `/auth/create-user/<user_type>`     | POST                | Register a patient or clinician    |
| `/auth/verify`                      | POST                | Verify an account                  |
| `/auth/login` · `/auth/logout`      | POST                | Session login / logout             |
| `/auth/clinician/login`             | POST                | Clinician login                    |
| `/auth/reset-password`              | POST                | Reset a password                   |
| `/api/mood/log`                     | POST                | Submit a daily mood entry          |
| `/api/mood/check-today`             | GET                 | Check whether today's entry exists |
| `/api/patient/<id>/mood-logs`       | GET                 | Retrieve a patient's mood logs     |
| `/api/patient/<id>/reference-lines` | GET/POST/PUT/DELETE | Manage chart reference lines       |
| `/api/connections/connect`          | POST                | Connect a patient and clinician    |

See [`doc/`](doc/) for the full authentication and CouchDB documentation.

## Documentation

| Document                                                 | Contents                          |
| -------------------------------------------------------- | --------------------------------- |
| [`doc/PROJECT_OVERVIEW.md`](doc/PROJECT_OVERVIEW.md)     | Architecture and feature overview |
| [`doc/AUTH_API.md`](doc/AUTH_API.md)                     | Patient authentication API        |
| [`doc/CLINICIAN_AUTH_API.md`](doc/CLINICIAN_AUTH_API.md) | Clinician authentication API      |
| [`doc/COUCHDB_SETUP.md`](doc/COUCHDB_SETUP.md)           | CouchDB setup guide               |
| [`doc/CONNECTIONS.md`](doc/CONNECTIONS.md)               | Patient–clinician connections     |

---

**Built by [rNLKJA](https://github.com/rNLKJA) for The University of Melbourne Psychiatry Department.**
