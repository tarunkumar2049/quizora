import re

import mysql.connector
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from extensions import bcrypt
from models.user_model import get_user_by_email
from utils.db import get_db_connection


auth_bp = Blueprint("auth", __name__)


def dashboard_url_for_role(role):
    """Return the correct dashboard endpoint for a user role."""

    if role == "admin":
        return url_for("dashboard.admin_dashboard")

    return url_for("dashboard.student_dashboard")


def is_valid_email(email):
    """Return True when the email has a simple valid format."""

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new student account."""

    if current_user.is_authenticated:
        return redirect(dashboard_url_for_role(current_user.role))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        if len(name) < 2:
            flash("Name must be at least 2 characters long.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("An account with this email already exists.", "warning")
                return render_template("auth/register.html", form_data=request.form)

            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, hashed_password, "student"),
            )
            connection.commit()

            flash("Registration successful. You can now log in.", "success")
            return redirect(url_for("auth.login"))

        except mysql.connector.Error:
            flash("Registration failed because the database is unavailable.", "danger")
            return render_template("auth/register.html", form_data=request.form)

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    return render_template("auth/register.html", form_data={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a student or admin and redirect by role."""

    if current_user.is_authenticated:
        return redirect(dashboard_url_for_role(current_user.role))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "1"

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("auth/login.html", form_data=request.form)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("auth/login.html", form_data=request.form)

        try:
            user = get_user_by_email(email)
        except mysql.connector.Error:
            flash("Login failed because the database is unavailable.", "danger")
            return render_template("auth/login.html", form_data=request.form)

        if not user or not bcrypt.check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form_data=request.form)

        login_user(user, remember=remember)
        flash("Logged in successfully.", "success")
        return redirect(dashboard_url_for_role(user.role))

    return render_template("auth/login.html", form_data={})


@auth_bp.route("/logout")
def logout():
    """End the current user session."""

    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "info")

    return redirect(url_for("auth.login"))
