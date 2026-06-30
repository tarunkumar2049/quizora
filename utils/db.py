import mysql.connector
from flask import current_app


def get_db_connection():
    """Create a new MySQL connection using the active Flask configuration."""

    return mysql.connector.connect(**current_app.config["MYSQL_CONFIG"])
