from utils.db import get_db_connection


def get_student_dashboard_data(user_id):
    """Collect all data needed for the student dashboard."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT COUNT(*) AS available_quizzes
            FROM quizzes
            WHERE status = %s
            """,
            ("active",),
        )
        available_quizzes_count = cursor.fetchone()["available_quizzes"]

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_attempts,
                COALESCE(AVG(accuracy), 0) AS average_accuracy,
                COALESCE(MAX(score), 0) AS best_score
            FROM results
            WHERE user_id = %s
            """,
            (user_id,),
        )
        summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT quiz_id, title, subject, duration_min
            FROM quizzes
            WHERE status = %s
            ORDER BY quiz_id DESC
            LIMIT 5
            """,
            ("active",),
        )
        available_quizzes = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                r.result_id,
                r.score,
                r.correct_answers,
                r.total_questions,
                r.accuracy,
                r.date,
                q.title AS quiz_title,
                q.subject
            FROM results r
            INNER JOIN quizzes q ON r.quiz_id = q.quiz_id
            WHERE r.user_id = %s
            ORDER BY r.date DESC
            LIMIT 5
            """,
            (user_id,),
        )
        recent_results = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                q.title AS quiz_title,
                r.accuracy,
                DATE_FORMAT(r.date, '%%d %%b') AS attempt_date
            FROM results r
            INNER JOIN quizzes q ON r.quiz_id = q.quiz_id
            WHERE r.user_id = %s
            ORDER BY r.date ASC
            LIMIT 10
            """,
            (user_id,),
        )
        progress_rows = cursor.fetchall()

        return {
            "summary": {
                "available_quizzes": available_quizzes_count,
                "total_attempts": summary["total_attempts"],
                "average_accuracy": round(float(summary["average_accuracy"]), 2),
                "best_score": summary["best_score"],
            },
            "available_quizzes": available_quizzes,
            "recent_results": recent_results,
            "progress_labels": [
                f"{row['quiz_title']} ({row['attempt_date']})" for row in progress_rows
            ],
            "progress_values": [float(row["accuracy"]) for row in progress_rows],
        }

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
