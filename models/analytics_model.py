from utils.db import get_db_connection


def get_admin_analytics_data():
    """Collect platform-wide analytics for admin charts."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_attempts,
                COALESCE(AVG(accuracy), 0) AS average_accuracy,
                COALESCE(SUM(correct_answers), 0) AS total_correct,
                COALESCE(SUM(total_questions), 0) AS total_questions
            FROM results
            """
        )
        summary_row = cursor.fetchone()
        total_correct = int(summary_row["total_correct"])
        total_questions = int(summary_row["total_questions"])
        total_incorrect = total_questions - total_correct

        cursor.execute(
            """
            SELECT
                q.title,
                q.subject,
                COUNT(r.result_id) AS attempts,
                COALESCE(AVG(r.accuracy), 0) AS average_accuracy
            FROM quizzes q
            LEFT JOIN results r ON q.quiz_id = r.quiz_id
            GROUP BY q.quiz_id, q.title, q.subject
            ORDER BY average_accuracy DESC, attempts DESC
            LIMIT 10
            """
        )
        quiz_performance = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                q.subject,
                COUNT(r.result_id) AS attempts,
                COALESCE(AVG(r.accuracy), 0) AS average_accuracy
            FROM quizzes q
            INNER JOIN results r ON q.quiz_id = r.quiz_id
            GROUP BY q.subject
            ORDER BY average_accuracy DESC
            """
        )
        subject_performance = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                questions.difficulty,
                COUNT(*) AS answered_count,
                SUM(CASE WHEN aa.is_correct = TRUE THEN 1 ELSE 0 END) AS correct_count,
                ROUND(
                    SUM(CASE WHEN aa.is_correct = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100,
                    2
                ) AS accuracy
            FROM attempt_answers aa
            INNER JOIN questions ON aa.question_id = questions.question_id
            GROUP BY questions.difficulty
            """
        )
        difficulty_rows = cursor.fetchall()
        difficulty_map = {
            row["difficulty"]: {
                "difficulty": row["difficulty"],
                "answered_count": row["answered_count"],
                "correct_count": row["correct_count"],
                "accuracy": float(row["accuracy"]),
            }
            for row in difficulty_rows
        }
        difficulty_performance = [
            difficulty_map.get(
                difficulty,
                {
                    "difficulty": difficulty,
                    "answered_count": 0,
                    "correct_count": 0,
                    "accuracy": 0,
                },
            )
            for difficulty in ["Easy", "Medium", "Hard"]
        ]

        cursor.execute(
            """
            SELECT
                DATE_FORMAT(date, '%%d %%b') AS attempt_date,
                COUNT(*) AS attempts,
                ROUND(AVG(accuracy), 2) AS average_accuracy
            FROM results
            GROUP BY DATE(date), DATE_FORMAT(date, '%%d %%b')
            ORDER BY DATE(date) ASC
            LIMIT 14
            """
        )
        attempt_trend = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                users.name AS student_name,
                COUNT(r.result_id) AS attempts,
                ROUND(AVG(r.accuracy), 2) AS average_accuracy,
                MAX(r.score) AS best_score
            FROM results r
            INNER JOIN users ON r.user_id = users.user_id
            GROUP BY users.user_id, users.name
            ORDER BY average_accuracy DESC, attempts DESC
            LIMIT 10
            """
        )
        student_leaderboard = cursor.fetchall()

        return {
            "summary": {
                "total_attempts": summary_row["total_attempts"],
                "average_accuracy": round(float(summary_row["average_accuracy"]), 2),
                "total_correct": total_correct,
                "total_incorrect": total_incorrect,
                "total_questions": total_questions,
            },
            "quiz_performance": quiz_performance,
            "subject_performance": subject_performance,
            "difficulty_performance": difficulty_performance,
            "attempt_trend": attempt_trend,
            "student_leaderboard": student_leaderboard,
            "chart_data": {
                "quiz_labels": [row["title"] for row in quiz_performance],
                "quiz_accuracy": [float(row["average_accuracy"]) for row in quiz_performance],
                "subject_labels": [row["subject"] for row in subject_performance],
                "subject_accuracy": [float(row["average_accuracy"]) for row in subject_performance],
                "difficulty_labels": [row["difficulty"] for row in difficulty_performance],
                "difficulty_accuracy": [row["accuracy"] for row in difficulty_performance],
                "attempt_labels": [row["attempt_date"] for row in attempt_trend],
                "attempt_counts": [row["attempts"] for row in attempt_trend],
                "attempt_accuracy": [float(row["average_accuracy"]) for row in attempt_trend],
                "correct_vs_incorrect": [total_correct, total_incorrect],
            },
        }

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
