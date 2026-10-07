# ESB Audit Portal

The ESB Audit Portal is an internal Flask application for tracing ESB transaction activity by ReqRef Number (RRN). It provides a browser-based search UI and a small JSON API for checking service-level audit records and payload timeline entries across Oracle-backed ESB environments.

## Overview

This tool is intended for internal support and QA workflows. It allows an operator to:

- search for an RRN in one of the configured ESB environments
- review recent service records and error data
- inspect a transaction timeline from the audit detail log
- keep database access read-only and limited to approved Oracle accounts

The browser UI calls the Flask application, which then uses the `oracledb` driver to query Oracle with fixed SQL and bind variables. Database credentials are configured per environment and are never returned by the API.

## Technology stack

- Python 3
- Flask
- Oracle Database via `oracledb`
- Bootstrap-based frontend

## Project structure

```text
app.py                  # app factory and server entry point
config.py               # environment configuration and validation
routes/
  audit_routes.py        # API endpoint definitions
services/
  audit_service.py       # validation and orchestration logic
db/
  oracle.py              # connection helpers
  queries.py             # centralized Oracle query definitions
static/
  js/app.js             # browser-side request handling and rendering
templates/
  index.html            # search UI
.env.example            # sample environment variables
requirements.txt        # Python dependencies
```

## Prerequisites

- Python 3.10+ recommended
- Access to the Oracle instance(s) used by the ESB environment
- A read-only database user for each environment that you enable

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the sample environment file and populate it with your Oracle connection details:

   ```bash
   cp .env.example .env
   ```

3. Update `.env` with the database credentials for each enabled environment. Each environment name in `ESB_ENVIRONMENTS` must match an `ENV_DB_*` configuration block.

   Example:

   ```env
   ESB_ENVIRONMENTS=UAT,PREPROD

   UAT_DB_USER=readonly_user
   UAT_DB_PASSWORD=secret
   UAT_DB_HOST=uat-db.example.com
   UAT_DB_PORT=1521
   UAT_DB_SERVICE=UATDB
   UAT_DB_SCHEMA=

   PREPROD_DB_USER=readonly_user
   PREPROD_DB_PASSWORD=secret
   PREPROD_DB_HOST=preprod-db.example.com
   PREPROD_DB_PORT=1521
   PREPROD_DB_SERVICE=PREPRODDB
   PREPROD_DB_SCHEMA=APP_SCHEMA

   FLASK_SECRET_KEY=replace-with-a-long-random-value
   LOG_LEVEL=INFO
   ```

4. Verify the Oracle column names and types with the DBA before production use. Update the query mappings in `db/queries.py` if the schema differs from the expected ESB audit tables.

5. Start the application:

   ```bash
   python app.py
   ```

6. Open the app in a browser:

   ```text
   http://127.0.0.1:5000
   ```

## Configuration rules

- `ESB_ENVIRONMENTS` is a comma-separated list of environment names.
- Each name requires matching `<ENV>_DB_USER`, `<ENV>_DB_PASSWORD`, `<ENV>_DB_HOST`, and `<ENV>_DB_SERVICE` variables.
- `<ENV>_DB_PORT` defaults to `1521` when omitted.
- For `UAT`, `DB_SCHEMA` may be left empty so Oracle queries use the connected user's default schema.
- For non-UAT environments such as `PREPROD`, `DB_SCHEMA` is required and should point to the schema owner of the ESB audit tables.
- `FLASK_SECRET_KEY` should be a long, random secret value in deployment; do not use a plaintext value in production when a secret manager is available.

## API

The application exposes a search endpoint for request automation and tests:

```http
POST /api/audit/search
Content-Type: application/json
```

Example request:

```json
{
  "rrn": "2109202610155291",
  "environment": "UAT",
  "range": "today"
}
```

Valid `range` values:

- `today`
- `3_days`
- `7_days`
- `30_days` (default selection in the UI)
- `custom`

For `custom`, include ISO-formatted `from_date` and `to_date` values. The service enforces a 31-day maximum custom range. The request body is validated before hitting Oracle.

Example custom-date payload:

```json
{
  "rrn": "2109202610155291",
  "environment": "PREPROD",
  "range": "custom",
  "from_date": "2026-01-01T00:00:00",
  "to_date": "2026-01-07T00:00:00"
}
```

## Response shape

The endpoint returns a JSON object with:

- `success`: boolean status
- `rrn`: searched ReqRef Number
- `environment`: selected environment
- `range`: selected range or `custom`
- `summary`: counts for ACE and DTL rows
- `services`: service-level audit rows
- `audit_timeline`: detail-log timeline entries

## Security and operational notes

- Use a dedicated read-only Oracle account for each environment.
- Do not commit `.env` files or database credentials to source control.
- Run the application on an internal network or behind a reverse proxy with HTTPS enabled.
- Keep logs focused on application events and avoid logging request payload contents or connection details.
- The app intentionally uses fixed SQL and bind variables instead of dynamic SQL construction.

## Deployment guidance

For production or shared environments:

- place the app behind the organization’s authenticated reverse proxy
- require HTTPS
- store secrets in the company secret manager or environment injection layer
- restrict access to authorized support users only
- keep the Oracle account read-only and scoped to the required schemas
