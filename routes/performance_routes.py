import mysql.connector
from flask import Blueprint, flash, render_template
from flask_login import current_user

from models.performance_model import get_performance_analysis
from utils.decorators import role_required


performance_bp = Blueprint("performance", __name__)


@performance_bp.route("/student/performance")
@role_required("student")
def performance_analysis():
    """Show performance analysis for the logged-in student."""

    try:
        analysis = get_performance_analysis(current_user.user_id)
    except mysql.connector.Error:
        flash("Performance analysis could not be loaded because the database is unavailable.", "danger")
        analysis = {
            "summary": {
                "total_attempts": 0,
                "total_correct": 0,
                "incorrect_answers": 0,
                "total_questions": 0,
                "overall_accuracy": 0,
                "average_accuracy": 0,
            },
            "topic_analysis": [],
            "difficulty_analysis": [
                {"difficulty": "Easy", "total_questions": 0, "correct_answers": 0, "accuracy": 0},
                {"difficulty": "Medium", "total_questions": 0, "correct_answers": 0, "accuracy": 0},
                {"difficulty": "Hard", "total_questions": 0, "correct_answers": 0, "accuracy": 0},
            ],
            "attempt_history": [],
            "progress_labels": [],
            "progress_values": [],
            "topic_labels": [],
            "topic_values": [],
            "correct_vs_incorrect": [0, 0],
        }

    return render_template("performance/analysis.html", analysis=analysis)
