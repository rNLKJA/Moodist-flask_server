# CouchDB Connection Setup

## Environment Variables

To connect to the CouchDB database, you need to set the following environment variables:

```
COUCHDB_URL=https://54.206.113.97:20001
COUCHDB_USER=moodist
COUCHDB_PASSWORD=UniversityofMelbourneMoodistTeam2024
COUCHDB_DB=moodist
```

## Setting Environment Variables

### Option 1: Create a .env file

Create a file named `.env` in the root directory of the project with the above environment variables.

### Option 2: Set environment variables in your terminal

```bash
# For Linux/macOS
export COUCHDB_URL=https://54.206.113.97:20001
export COUCHDB_USER=moodist
export COUCHDB_PASSWORD=UniversityofMelbourneMoodistTeam2024
export COUCHDB_DB=moodist

# For Windows Command Prompt
set COUCHDB_URL=https://54.206.113.97:20001
set COUCHDB_USER=moodist
set COUCHDB_PASSWORD=UniversityofMelbourneMoodistTeam2024
set COUCHDB_DB=moodist

# For Windows PowerShell
$env:COUCHDB_URL="https://54.206.113.97:20001"
$env:COUCHDB_USER="moodist"
$env:COUCHDB_PASSWORD="UniversityofMelbourneMoodistTeam2024"
$env:COUCHDB_DB="moodist"
```

## Testing the Connection

To test the connection, use the following API endpoints:

1. Check environment variables:
   ```
   GET http://localhost:5000/api/connection/env
   ```

2. Test the connection:
   ```
   GET http://localhost:5000/api/connection/test
   ```

These endpoints will provide detailed information about the connection status and any errors that may occur. 