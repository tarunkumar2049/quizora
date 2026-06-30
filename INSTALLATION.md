# Quizora Installation Instructions

Quizora is a Flask + MySQL project for smart online quizzes and performance analysis.

## 1. Project Structure

Place the files and folders like this:

```text
Quizora/
├── app.py
├── config.py
├── requirements.txt
├── INSTALLATION.md
├── database/
│   └── schema.sql
├── models/
├── routes/
├── utils/
├── templates/
└── static/
    ├── css/
    ├── js/
    └── images/
```

## 2. Create a Virtual Environment

Open a terminal inside the `Quizora` folder.

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Create the MySQL Database

Make sure MySQL Server is running, then execute the schema file:

```bash
mysql -u root -p < database/schema.sql
```

This creates the `quizora_db` database and all required tables.

## 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-strong-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=quizora_db
FLASK_ENV=development
```

## 6. Run the Application

```bash
python app.py
```

Open this URL in your browser:

```text
http://127.0.0.1:5000
```

To test database connectivity after creating the database, visit:

```text
http://127.0.0.1:5000/db-check
```

## 7. Current Step Status

Step 1 is complete. The next step should add the first functional module without replacing these foundation files unless a small extension is required.
