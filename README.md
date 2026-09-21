# ESB Audit Portal

Internal Flask application for self-service ESB audit lookups by ReqRef Number. The browser communicates only with Flask; Flask uses the `oracledb` driver and a read-only Oracle account configured per environment.

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env`, then populate the database settings for each enabled environment. Keep the account read-only and never commit `.env`.
3. Verify the exact Oracle column names and datatypes with the DBA. Update the centralized mappings in `db/queries.py` if needed.
4. Start the application:

   ```bash
   python app.py
   ```

Open `http://127.0.0.1:5000`.

## Configuration

`ESB_ENVIRONMENTS` controls the selectable environments. Each comma-separated name needs matching `<ENV>_DB_USER`, `_PASSWORD`, `_HOST`, `_PORT`, and `_SERVICE` entries. Credentials are never returned by the API.

## API

`POST /api/audit/search` accepts JSON such as:

```json
{"rrn":"2109202610155291","environment":"UAT","range":"today"}
```

For `custom`, include ISO-format `from_date` and `to_date`; ranges are limited to 31 days. Queries use fixed SQL and Oracle bind variables. The application intentionally does not log payload content or connection details.

## Deployment notes

Run behind the organization’s authenticated reverse proxy and HTTPS in production. Set a long, random `FLASK_SECRET_KEY`; use the organization’s secret manager or protected environment injection rather than a plaintext `.env` where available.
