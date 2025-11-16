# Financial Hub

Financial Hub is a lightweight Flask application that unifies budget tracking and retirement planning. Upload CSV statements to import transactions, manage category-based budgets, and monitor retirement goals with a single dashboard backed by SQLite.

## Features
- **Statement ingestion** – Upload CSV files (date, description, amount, category) to store transactions per account.
- **Budgeting** – Define monthly category limits and compare against imported transactions.
- **Retirement planning** – Track current savings, contributions, expected return rate, and months-to-goal projection.
- **Lightweight UI** – Responsive dashboard built with server-rendered templates and minimal CSS.
- **SQLite persistence** – SQLAlchemy models with migrations ensure data durability out of the box.

## Getting Started

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize the database**
   ```bash
   flask --app run db upgrade
   ```

3. **Run the development server**
   ```bash
   flask --app run run --debug
   ```

4. **Use the dashboard**
   - Visit `http://127.0.0.1:5000`.
   - Upload a CSV statement with the columns `date` (`YYYY-MM-DD`), `description`, `amount`, and `category`.
   - Add budgets per category and update your retirement targets to see projections.

## Project Structure
```
app/
  __init__.py      # Flask application factory and configuration
  models.py        # SQLAlchemy models for accounts, budgets, transactions, retirement plans
  routes.py        # Routes for dashboard, file upload, budgeting, retirement plan updates
  templates/       # Jinja templates for the UI
  static/          # CSS styles
migrations/        # Alembic environment and versioned migrations
run.py             # WSGI entry point
requirements.txt   # Python dependencies
Dockerfile         # Production image definition
docker-compose.yml # Local orchestration for the container image
```

## CSV Format Example
```csv
date,description,amount,category
2024-01-01,Paycheck,2500,Income
2024-01-03,Rent,-1200,Housing
2024-01-05,Grocery Store,-150,Food
```

## Environment Variables
- `DATABASE_URL` – Override the default SQLite database path.
- `SECRET_KEY` – Set a production-ready secret key for Flask sessions.
- `UPLOAD_FOLDER` – Optional path for storing uploaded statements.

## Deployment

### Build a production image

Use the provided `Dockerfile` to produce a container image that runs the app with Gunicorn:

```bash
docker build -t financial-hub .
```

### Run with Docker Compose

To keep the SQLite database on a named volume and expose the service on port 8000:

```bash
docker compose up --build
```

The compose file automatically applies Alembic migrations (or falls back to `db.create_all()` on a fresh install) and then starts Gunicorn.

### Manual container run

If you prefer to run the image directly:

```bash
docker run -it --rm -p 8000:8000 -v financial-hub-data:/data financial-hub
```

Environment variables such as `DATABASE_URL`, `SECRET_KEY`, and `FLASK_ENV` can be supplied with `-e` flags.

## Testing
You can extend the project with unit tests using `pytest` or Flask’s built-in test client as needed. For smoke testing of the current codebase, run:

```bash
python -m compileall app run.py
```
