import mysql.connector
from flask import Blueprint, flash, render_template
from flask_login import current_user

from models.admin_dashboard_model import get_admin_dashboard_data
from models.student_dashboard_model import get_student_dashboard_data
from utils.decorators import role_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/student/dashboard")
@role_required("student")
def student_dashboard():
    """Show the student's dashboard with quiz and performance summary."""

    try:
        dashboard_data = get_student_dashboard_data(current_user.user_id)
    except mysql.connector.Error:
        flash("Dashboard data could not be loaded because the database is unavailable.", "danger")
        dashboard_data = {
            "summary": {
                "available_quizzes": 0,
                "total_attempts": 0,
                "average_accuracy": 0,
                "best_score": 0,
            },
            "available_quizzes": [],
            "recent_results": [],
            "progress_labels": [],
            "progress_values": [],
        }

    return render_template("dashboard/student_dashboard.html", data=dashboard_data)


@dashboard_bp.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    """Show the admin dashboard with platform-wide summary data."""

    try:
        dashboard_data = get_admin_dashboard_data()
    except mysql.connector.Error:
        flash("Admin dashboard data could not be loaded because the database is unavailable.", "danger")
        dashboard_data = {
            "summary": {
                "total_users": 0,
                "total_students": 0,
                "total_admins": 0,
                "total_quizzes": 0,
                "active_quizzes": 0,
                "total_questions": 0,
                "total_attempts": 0,
                "average_accuracy": 0,
            },
            "recent_quizzes": [],
            "recent_users": [],
            "recent_results": [],
        }

    return render_template("dashboard/admin_dashboard.html", data=dashboard_data)
