from utils.db import get_db_connection


def get_admin_dashboard_data():
    """Collect summary data for the admin dashboard."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("SELECT COUNT(*) AS total_students FROM users WHERE role = %s", ("student",))
        total_students = cursor.fetchone()["total_students"]

        cursor.execute("SELECT COUNT(*) AS total_admins FROM users WHERE role = %s", ("admin",))
        total_admins = cursor.fetchone()["total_admins"]

        cursor.execute("SELECT COUNT(*) AS total_quizzes FROM quizzes")
        total_quizzes = cursor.fetchone()["total_quizzes"]

        cursor.execute("SELECT COUNT(*) AS active_quizzes FROM quizzes WHERE status = %s", ("active",))
        active_quizzes = cursor.fetchone()["active_quizzes"]

        cursor.execute("SELECT COUNT(*) AS total_questions FROM questions")
        total_questions = cursor.fetchone()["total_questions"]

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_attempts,
                COALESCE(AVG(accuracy), 0) AS average_accuracy
            FROM results
            """
        )
        result_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT quiz_id, title, subject, duration_min, status
            FROM quizzes
            ORDER BY quiz_id DESC
            LIMIT 5
            """
        )
        recent_quizzes = cursor.fetchall()

        cursor.execute(
            """
            SELECT user_id, name, email, role, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        recent_users = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                r.result_id,
                r.score,
                r.accuracy,
                r.date,
                u.name AS student_name,
                q.title AS quiz_title
            FROM results r
            INNER JOIN users u ON r.user_id = u.user_id
            INNER JOIN quizzes q ON r.quiz_id = q.quiz_id
            ORDER BY r.date DESC
            LIMIT 5
            """
        )
        recent_results = cursor.fetchall()

        return {
            "summary": {
                "total_users": total_users,
                "total_students": total_students,
                "total_admins": total_admins,
                "total_quizzes": total_quizzes,
                "active_quizzes": active_quizzes,
                "total_questions": total_questions,
                "total_attempts": result_summary["total_attempts"],
                "average_accuracy": round(float(result_summary["average_accuracy"]), 2),
            },
            "recent_quizzes": recent_quizzes,
            "recent_users": recent_users,
            "recent_results": recent_results,
        }

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
