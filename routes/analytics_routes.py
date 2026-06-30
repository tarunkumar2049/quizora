import mysql.connector
from flask import Blueprint, flash, jsonify, render_template

from models.analytics_model import get_admin_analytics_data
from utils.decorators import role_required


analytics_bp = Blueprint("analytics", __name__)


def empty_analytics_data():
    """Return empty analytics data when the database cannot be reached."""

    return {
        "summary": {
            "total_attempts": 0,
            "average_accuracy": 0,
            "total_correct": 0,
            "total_incorrect": 0,
            "total_questions": 0,
        },
        "quiz_performance": [],
        "subject_performance": [],
        "difficulty_performance": [
            {"difficulty": "Easy", "answered_count": 0, "correct_count": 0, "accuracy": 0},
            {"difficulty": "Medium", "answered_count": 0, "correct_count": 0, "accuracy": 0},
            {"difficulty": "Hard", "answered_count": 0, "correct_count": 0, "accuracy": 0},
        ],
        "attempt_trend": [],
        "student_leaderboard": [],
        "chart_data": {
            "quiz_labels": [],
            "quiz_accuracy": [],
            "subject_labels": [],
            "subject_accuracy": [],
            "difficulty_labels": ["Easy", "Medium", "Hard"],
            "difficulty_accuracy": [0, 0, 0],
            "attempt_labels": [],
            "attempt_counts": [],
            "attempt_accuracy": [],
            "correct_vs_incorrect": [0, 0],
        },
    }


@analytics_bp.route("/admin/analytics")
@role_required("admin")
def admin_analytics():
    """Show charts and analytics for admins."""

    try:
        analytics = get_admin_analytics_data()
    except mysql.connector.Error:
        flash("Analytics could not be loaded because the database is unavailable.", "danger")
        analytics = empty_analytics_data()

    return render_template("analytics/admin_analytics.html", analytics=analytics)


@analytics_bp.route("/admin/analytics/data")
@role_required("admin")
def admin_analytics_data():
    """Return analytics chart data as JSON for future dynamic updates."""

    try:
        analytics = get_admin_analytics_data()
    except mysql.connector.Error:
        return jsonify(empty_analytics_data()["chart_data"]), 500

    return jsonify(analytics["chart_data"])
