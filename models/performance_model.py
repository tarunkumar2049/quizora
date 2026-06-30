from utils.db import get_db_connection


def get_recommendation_message(accuracy):
    """Return a recommendation based on an accuracy percentage."""

    if accuracy < 50:
        return "Your accuracy in this topic is low. Revisit the fundamentals."

    if accuracy <= 70:
        return "Needs improvement."

    return "Good understanding."


def get_performance_analysis(user_id):
    """Collect performance analysis data for a student."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_attempts,
                COALESCE(SUM(correct_answers), 0) AS total_correct,
                COALESCE(SUM(total_questions), 0) AS total_questions,
                COALESCE(AVG(accuracy), 0) AS average_accuracy
            FROM results
            WHERE user_id = %s
            """,
            (user_id,),
        )
        summary_row = cursor.fetchone()
        total_correct = int(summary_row["total_correct"])
        total_questions = int(summary_row["total_questions"])
        incorrect_answers = total_questions - total_correct
        overall_accuracy = round((total_correct / total_questions * 100), 2) if total_questions else 0

        cursor.execute(
            """
            SELECT
                q.category,
                COUNT(*) AS total_questions,
                SUM(CASE WHEN aa.is_correct = TRUE THEN 1 ELSE 0 END) AS correct_answers,
                ROUND(
                    SUM(CASE WHEN aa.is_correct = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100,
                    2
                ) AS accuracy
            FROM attempt_answers aa
            INNER JOIN results r ON aa.result_id = r.result_id
            INNER JOIN questions q ON aa.question_id = q.question_id
            WHERE r.user_id = %s
            GROUP BY q.category
            ORDER BY accuracy ASC, q.category ASC
            """,
            (user_id,),
        )
        topic_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                q.difficulty,
                COUNT(*) AS total_questions,
                SUM(CASE WHEN aa.is_correct = TRUE THEN 1 ELSE 0 END) AS correct_answers,
                ROUND(
                    SUM(CASE WHEN aa.is_correct = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100,
                    2
                ) AS accuracy
            FROM attempt_answers aa
            INNER JOIN results r ON aa.result_id = r.result_id
            INNER JOIN questions q ON aa.question_id = q.question_id
            WHERE r.user_id = %s
            GROUP BY q.difficulty
            """,
            (user_id,),
        )
        difficulty_rows = cursor.fetchall()
        difficulty_map = {
            row["difficulty"]: {
                "difficulty": row["difficulty"],
                "total_questions": row["total_questions"],
                "correct_answers": row["correct_answers"],
                "accuracy": float(row["accuracy"]),
            }
            for row in difficulty_rows
        }
        difficulty_analysis = [
            difficulty_map.get(
                difficulty,
                {
                    "difficulty": difficulty,
                    "total_questions": 0,
                    "correct_answers": 0,
                    "accuracy": 0,
                },
            )
            for difficulty in ["Easy", "Medium", "Hard"]
        ]

        cursor.execute(
            """
            SELECT
                r.result_id,
                r.score,
                r.correct_answers,
                r.total_questions,
                r.accuracy,
                r.date,
                quiz.title AS quiz_title,
                quiz.subject
            FROM results r
            INNER JOIN quizzes quiz ON r.quiz_id = quiz.quiz_id
            WHERE r.user_id = %s
            ORDER BY r.date DESC
            """,
            (user_id,),
        )
        attempt_history = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                quiz.title AS quiz_title,
                r.accuracy,
                DATE_FORMAT(r.date, '%%d %%b') AS attempt_date
            FROM results r
            INNER JOIN quizzes quiz ON r.quiz_id = quiz.quiz_id
            WHERE r.user_id = %s
            ORDER BY r.date ASC
            """,
            (user_id,),
        )
        progress_rows = cursor.fetchall()

        topic_analysis = []
        for row in topic_rows:
            accuracy = float(row["accuracy"])
            topic_analysis.append(
                {
                    "category": row["category"],
                    "total_questions": row["total_questions"],
                    "correct_answers": row["correct_answers"],
                    "accuracy": accuracy,
                    "recommendation": get_recommendation_message(accuracy),
                }
            )

        return {
            "summary": {
                "total_attempts": summary_row["total_attempts"],
                "total_correct": total_correct,
                "incorrect_answers": incorrect_answers,
                "total_questions": total_questions,
                "overall_accuracy": overall_accuracy,
                "average_accuracy": round(float(summary_row["average_accuracy"]), 2),
            },
            "topic_analysis": topic_analysis,
            "difficulty_analysis": difficulty_analysis,
            "attempt_history": attempt_history,
            "progress_labels": [
                f"{row['quiz_title']} ({row['attempt_date']})" for row in progress_rows
            ],
            "progress_values": [float(row["accuracy"]) for row in progress_rows],
            "topic_labels": [row["category"] for row in topic_analysis],
            "topic_values": [row["accuracy"] for row in topic_analysis],
            "correct_vs_incorrect": [total_correct, incorrect_answers],
        }

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
