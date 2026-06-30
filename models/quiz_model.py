from utils.db import get_db_connection
from utils.result_calculator import calculate_quiz_result


def get_all_quizzes():
    """Return all quizzes with question counts for admin screens."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                q.quiz_id,
                q.title,
                q.subject,
                q.duration_min,
                q.status,
                u.name AS created_by_name,
                COUNT(questions.question_id) AS question_count
            FROM quizzes q
            INNER JOIN users u ON q.created_by = u.user_id
            LEFT JOIN questions ON q.quiz_id = questions.quiz_id
            GROUP BY q.quiz_id, q.title, q.subject, q.duration_min, q.status, u.name
            ORDER BY q.quiz_id DESC
            """
        )
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_active_quizzes():
    """Return active quizzes visible to students."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                q.quiz_id,
                q.title,
                q.subject,
                q.duration_min,
                COUNT(questions.question_id) AS question_count
            FROM quizzes q
            LEFT JOIN questions ON q.quiz_id = questions.quiz_id
            WHERE q.status = %s
            GROUP BY q.quiz_id, q.title, q.subject, q.duration_min
            ORDER BY q.quiz_id DESC
            """,
            ("active",),
        )
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_quiz_by_id(quiz_id):
    """Return one quiz by ID."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT quiz_id, title, subject, duration_min, created_by, status
            FROM quizzes
            WHERE quiz_id = %s
            """,
            (quiz_id,),
        )
        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def create_quiz(title, subject, duration_min, created_by, status):
    """Create a new quiz."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO quizzes (title, subject, duration_min, created_by, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, subject, duration_min, created_by, status),
        )
        connection.commit()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def update_quiz(quiz_id, title, subject, duration_min, status):
    """Update an existing quiz."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE quizzes
            SET title = %s, subject = %s, duration_min = %s, status = %s
            WHERE quiz_id = %s
            """,
            (title, subject, duration_min, status, quiz_id),
        )
        connection.commit()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def delete_quiz(quiz_id):
    """Delete a quiz and its related questions/options through cascades."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        connection.commit()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_questions_for_quiz(quiz_id):
    """Return questions and their options for a quiz."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT question_id, quiz_id, question_text, category, difficulty, explanation
            FROM questions
            WHERE quiz_id = %s
            ORDER BY question_id ASC
            """,
            (quiz_id,),
        )
        questions = cursor.fetchall()

        for question in questions:
            cursor.execute(
                """
                SELECT option_id, question_id, option_text, is_correct
                FROM options
                WHERE question_id = %s
                ORDER BY option_id ASC
                """,
                (question["question_id"],),
            )
            question["options"] = cursor.fetchall()

        return questions

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_question_with_options(question_id):
    """Return a single question and its options."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT question_id, quiz_id, question_text, category, difficulty, explanation
            FROM questions
            WHERE question_id = %s
            """,
            (question_id,),
        )
        question = cursor.fetchone()

        if not question:
            return None

        cursor.execute(
            """
            SELECT option_id, option_text, is_correct
            FROM options
            WHERE question_id = %s
            ORDER BY option_id ASC
            """,
            (question_id,),
        )
        question["options"] = cursor.fetchall()
        return question

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def create_question(quiz_id, question_text, category, difficulty, explanation, option_texts, correct_index):
    """Create one question with four options."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO questions (quiz_id, question_text, category, difficulty, explanation)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (quiz_id, question_text, category, difficulty, explanation),
        )
        question_id = cursor.lastrowid

        for index, option_text in enumerate(option_texts):
            cursor.execute(
                """
                INSERT INTO options (question_id, option_text, is_correct)
                VALUES (%s, %s, %s)
                """,
                (question_id, option_text, index == correct_index),
            )

        connection.commit()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def update_question(question_id, question_text, category, difficulty, explanation, option_data, correct_option_id):
    """Update one question and its four options."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE questions
            SET question_text = %s, category = %s, difficulty = %s, explanation = %s
            WHERE question_id = %s
            """,
            (question_text, category, difficulty, explanation, question_id),
        )

        for option in option_data:
            cursor.execute(
                """
                UPDATE options
                SET option_text = %s, is_correct = %s
                WHERE option_id = %s AND question_id = %s
                """,
                (
                    option["option_text"],
                    option["option_id"] == correct_option_id,
                    option["option_id"],
                    question_id,
                ),
            )

        connection.commit()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def delete_question(question_id):
    """Delete a question and its options through cascade rules."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM questions WHERE question_id = %s", (question_id,))
        connection.commit()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def submit_quiz_attempt(user_id, quiz_id, submitted_answers):
    """Score a quiz attempt and store the result plus selected answers."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        questions = get_questions_for_quiz(quiz_id)
        result = calculate_quiz_result(questions, submitted_answers)

        cursor.execute(
            """
            INSERT INTO results
                (user_id, quiz_id, score, correct_answers, total_questions, accuracy)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                quiz_id,
                result["score"],
                result["correct_answers"],
                result["total_questions"],
                result["accuracy"],
            ),
        )
        result_id = cursor.lastrowid

        for answer in result["scored_answers"]:
            cursor.execute(
                """
                INSERT INTO attempt_answers
                    (result_id, question_id, selected_option, is_correct)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    result_id,
                    answer["question_id"],
                    answer["selected_option"],
                    answer["is_correct"],
                ),
            )

        connection.commit()
        return result_id

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_result_summary(result_id, user_id):
    """Return a stored result for the current student."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                r.result_id,
                r.score,
                r.correct_answers,
                (r.total_questions - r.correct_answers) AS incorrect_answers,
                r.total_questions,
                r.accuracy,
                r.date,
                q.title,
                q.subject
            FROM results r
            INNER JOIN quizzes q ON r.quiz_id = q.quiz_id
            WHERE r.result_id = %s AND r.user_id = %s
            """,
            (result_id, user_id),
        )
        return cursor.fetchone()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_result_details(result_id, user_id):
    """Return a result summary with answer-by-answer calculation details."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                r.result_id,
                r.score,
                r.correct_answers,
                (r.total_questions - r.correct_answers) AS incorrect_answers,
                r.total_questions,
                r.accuracy,
                r.date,
                q.title,
                q.subject
            FROM results r
            INNER JOIN quizzes q ON r.quiz_id = q.quiz_id
            WHERE r.result_id = %s AND r.user_id = %s
            """,
            (result_id, user_id),
        )
        summary = cursor.fetchone()

        if not summary:
            return None

        cursor.execute(
            """
            SELECT
                aa.answer_id,
                aa.is_correct,
                q.question_id,
                q.question_text,
                q.category,
                q.difficulty,
                q.explanation,
                selected_options.option_text AS selected_answer,
                correct_options.option_text AS correct_answer
            FROM attempt_answers aa
            INNER JOIN questions q ON aa.question_id = q.question_id
            LEFT JOIN options selected_options
                ON aa.selected_option = selected_options.option_id
            LEFT JOIN options correct_options
                ON correct_options.question_id = q.question_id
                AND correct_options.is_correct = TRUE
            WHERE aa.result_id = %s
            ORDER BY q.question_id ASC
            """,
            (result_id,),
        )
        answers = cursor.fetchall()

        return {
            "summary": summary,
            "answers": answers,
        }

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
