# Financial Hub

Financial Hub is a lightweight Flask application that unifies budget tracking and retirement planning. Upload CSV statements to
import transactions, manage category-based budgets, and monitor retirement goals with a single dashboard backed by SQLite.

The project now also ships with a production-ready Docker image definition so you can deploy the service anywhere that runs containers.

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
   flask --app run db init
   flask --app run db migrate -m "Initial tables"
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
run.py             # WSGI entry point
requirements.txt   # Python dependencies
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

## Containerized Deployment

Financial Hub includes a Dockerfile and docker-compose definition for reproducible deployments:

1. **Build the image**
   ```bash
   docker build -t financial-hub .
   ```

2. **Run locally with Docker Compose**
   ```bash
   docker compose up --build
   ```

   The service listens on `http://localhost:8000` and persists SQLite data plus uploads in the mounted `instance` volume.

3. **Deploy to your infrastructure**
   - Push the generated container image to your registry of choice.
   - Set `SECRET_KEY`, `DATABASE_URL` (e.g., pointing to PostgreSQL), and any other environment variables in your hosting platform.
   - The container entrypoint automatically applies migrations when a `migrations/` directory exists, then starts Gunicorn bound to port 8000. If your hosting platform provides a `PORT` variable, it will be honored automatically via `gunicorn --bind 0.0.0.0:$PORT`.

> **Tip:** For platforms such as Render, Fly.io, or Azure Container Apps, simply reference the built image and expose port `8000`.

## Testing
You can extend the project with unit tests using `pytest` or Flask’s built-in test client as needed.
