# Quizora Deployment Guide

This guide covers local final checks and a simple production-style deployment for the Flask + MySQL Quizora web app.

## 1. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure Environment Variables

Copy `.env.example` to `.env` and update the values.

```env
SECRET_KEY=replace-with-a-strong-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=quizora_db
FLASK_ENV=production
```

Use a long random `SECRET_KEY` in production.

## 3. Create the Database

```bash
mysql -u root -p < database/schema.sql
```

## 4. Run Locally

For development:

```bash
python app.py
```

For a production-style local run on Linux/macOS:

```bash
gunicorn wsgi:app
```

On Windows, use `python app.py` for local testing. Most production hosts run Gunicorn on Linux.

## 5. Deployment Notes

- Set `FLASK_ENV=production`.
- Set a secure `SECRET_KEY`.
- Use a hosted MySQL database or a server-managed MySQL instance.
- Run `database/schema.sql` before first use.
- Use `wsgi.py` as the application entry point.
- Use the `Procfile` command when deploying to platforms that support it.

## 6. Health Checks

After deployment, test:

```text
/health
/db-check
```

`/health` confirms Flask is responding. `/db-check` confirms MySQL connectivity.
