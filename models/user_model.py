from flask_login import UserMixin

from utils.db import get_db_connection


class User(UserMixin):
    """Application user object used by Flask-Login."""

    def __init__(self, user_id, name, email, password, role):
        self.id = str(user_id)
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    @staticmethod
    def from_row(row):
        """Build a User object from a database row."""

        if not row:
            return None

        return User(
            user_id=row["user_id"],
            name=row["name"],
            email=row["email"],
            password=row["password"],
            role=row["role"],
        )


def get_user_by_id(user_id):
    """Fetch one user by primary key."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT user_id, name, email, password, role
            FROM users
            WHERE user_id = %s
            """,
            (user_id,),
        )
        return User.from_row(cursor.fetchone())

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_user_by_email(email):
    """Fetch one user by email address."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT user_id, name, email, password, role
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        return User.from_row(cursor.fetchone())

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
