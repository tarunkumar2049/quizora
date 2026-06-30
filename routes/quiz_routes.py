import mysql.connector
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from models.quiz_model import (
    create_question,
    create_quiz,
    delete_question,
    delete_quiz,
    get_active_quizzes,
    get_all_quizzes,
    get_question_with_options,
    get_questions_for_quiz,
    get_quiz_by_id,
    get_result_details,
    submit_quiz_attempt,
    update_question,
    update_quiz,
)
from utils.decorators import role_required


quiz_bp = Blueprint("quiz", __name__)


def validate_quiz_form(form):
    """Validate quiz create/edit form data."""

    title = form.get("title", "").strip()
    subject = form.get("subject", "").strip()
    duration_text = form.get("duration_min", "").strip()
    status = form.get("status", "active").strip()

    if not title or not subject or not duration_text:
        return None, "Title, subject, and duration are required."

    if status not in ["active", "inactive"]:
        return None, "Invalid quiz status."

    try:
        duration_min = int(duration_text)
    except ValueError:
        return None, "Duration must be a number."

    if duration_min < 1:
        return None, "Duration must be at least 1 minute."

    return {
        "title": title,
        "subject": subject,
        "duration_min": duration_min,
        "status": status,
    }, None


def validate_question_form(form, editing=False):
    """Validate question form data for create and edit screens."""

    question_text = form.get("question_text", "").strip()
    category = form.get("category", "").strip()
    difficulty = form.get("difficulty", "Easy").strip()
    explanation = form.get("explanation", "").strip()

    if not question_text or not category:
        return None, "Question text and category are required."

    if difficulty not in ["Easy", "Medium", "Hard"]:
        return None, "Invalid difficulty."

    if editing:
        option_ids = form.getlist("option_id")
        option_texts = form.getlist("option_text")
        correct_option_id = form.get("correct_option")

        if len(option_ids) != 4 or len(option_texts) != 4:
            return None, "A question must have exactly four options."

        if correct_option_id not in option_ids:
            return None, "Please choose the correct option."

        for option_text in option_texts:
            if not option_text.strip():
                return None, "All four options are required."

        return {
            "question_text": question_text,
            "category": category,
            "difficulty": difficulty,
            "explanation": explanation,
            "option_data": [
                {"option_id": int(option_ids[index]), "option_text": option_texts[index].strip()}
                for index in range(4)
            ],
            "correct_option_id": int(correct_option_id),
        }, None

    option_texts = [
        form.get("option_1", "").strip(),
        form.get("option_2", "").strip(),
        form.get("option_3", "").strip(),
        form.get("option_4", "").strip(),
    ]
    correct_option = form.get("correct_option")

    if any(not option_text for option_text in option_texts):
        return None, "All four options are required."

    if correct_option not in ["0", "1", "2", "3"]:
        return None, "Please choose the correct option."

    return {
        "question_text": question_text,
        "category": category,
        "difficulty": difficulty,
        "explanation": explanation,
        "option_texts": option_texts,
        "correct_index": int(correct_option),
    }, None


@quiz_bp.route("/admin/quizzes")
@role_required("admin")
def admin_quizzes():
    """List quizzes for admins."""

    try:
        quizzes = get_all_quizzes()
    except mysql.connector.Error:
        flash("Quizzes could not be loaded because the database is unavailable.", "danger")
        quizzes = []

    return render_template("quiz/admin_quizzes.html", quizzes=quizzes)


@quiz_bp.route("/admin/quizzes/create", methods=["GET", "POST"])
@role_required("admin")
def create_quiz_view():
    """Create a quiz."""

    if request.method == "POST":
        quiz_data, error = validate_quiz_form(request.form)

        if error:
            flash(error, "danger")
            return render_template("quiz/quiz_form.html", quiz=request.form, mode="create")

        try:
            create_quiz(
                quiz_data["title"],
                quiz_data["subject"],
                quiz_data["duration_min"],
                current_user.user_id,
                quiz_data["status"],
            )
            flash("Quiz created successfully.", "success")
            return redirect(url_for("quiz.admin_quizzes"))
        except mysql.connector.Error:
            flash("Quiz could not be created because the database is unavailable.", "danger")

    return render_template("quiz/quiz_form.html", quiz={}, mode="create")


@quiz_bp.route("/admin/quizzes/<int:quiz_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_quiz_view(quiz_id):
    """Edit a quiz."""

    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        flash("Quiz not found.", "warning")
        return redirect(url_for("quiz.admin_quizzes"))

    if request.method == "POST":
        quiz_data, error = validate_quiz_form(request.form)

        if error:
            flash(error, "danger")
            return render_template("quiz/quiz_form.html", quiz=request.form, mode="edit")

        try:
            update_quiz(
                quiz_id,
                quiz_data["title"],
                quiz_data["subject"],
                quiz_data["duration_min"],
                quiz_data["status"],
            )
            flash("Quiz updated successfully.", "success")
            return redirect(url_for("quiz.admin_quizzes"))
        except mysql.connector.Error:
            flash("Quiz could not be updated because the database is unavailable.", "danger")

    return render_template("quiz/quiz_form.html", quiz=quiz, mode="edit")


@quiz_bp.route("/admin/quizzes/<int:quiz_id>/delete", methods=["POST"])
@role_required("admin")
def delete_quiz_view(quiz_id):
    """Delete a quiz."""

    try:
        delete_quiz(quiz_id)
        flash("Quiz deleted successfully.", "success")
    except mysql.connector.Error:
        flash("Quiz could not be deleted because it may already have submitted results.", "danger")

    return redirect(url_for("quiz.admin_quizzes"))


@quiz_bp.route("/admin/quizzes/<int:quiz_id>/questions")
@role_required("admin")
def manage_questions(quiz_id):
    """List questions for a quiz."""

    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        flash("Quiz not found.", "warning")
        return redirect(url_for("quiz.admin_quizzes"))

    try:
        questions = get_questions_for_quiz(quiz_id)
    except mysql.connector.Error:
        flash("Questions could not be loaded because the database is unavailable.", "danger")
        questions = []

    return render_template("quiz/manage_questions.html", quiz=quiz, questions=questions)


@quiz_bp.route("/admin/quizzes/<int:quiz_id>/questions/add", methods=["GET", "POST"])
@role_required("admin")
def add_question_view(quiz_id):
    """Add a question to a quiz."""

    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        flash("Quiz not found.", "warning")
        return redirect(url_for("quiz.admin_quizzes"))

    if request.method == "POST":
        question_data, error = validate_question_form(request.form)

        if error:
            flash(error, "danger")
            return render_template(
                "quiz/question_form.html",
                quiz=quiz,
                question=request.form,
                mode="create",
            )

        try:
            create_question(
                quiz_id,
                question_data["question_text"],
                question_data["category"],
                question_data["difficulty"],
                question_data["explanation"],
                question_data["option_texts"],
                question_data["correct_index"],
            )
            flash("Question added successfully.", "success")
            return redirect(url_for("quiz.manage_questions", quiz_id=quiz_id))
        except mysql.connector.Error:
            flash("Question could not be added because the database is unavailable.", "danger")

    return render_template("quiz/question_form.html", quiz=quiz, question={}, mode="create")


@quiz_bp.route("/admin/questions/<int:question_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_question_view(question_id):
    """Edit a question and its options."""

    question = get_question_with_options(question_id)
    if not question:
        flash("Question not found.", "warning")
        return redirect(url_for("quiz.admin_quizzes"))

    quiz = get_quiz_by_id(question["quiz_id"])

    if request.method == "POST":
        question_data, error = validate_question_form(request.form, editing=True)

        if error:
            flash(error, "danger")
            return render_template(
                "quiz/question_form.html",
                quiz=quiz,
                question=question,
                mode="edit",
            )

        try:
            update_question(
                question_id,
                question_data["question_text"],
                question_data["category"],
                question_data["difficulty"],
                question_data["explanation"],
                question_data["option_data"],
                question_data["correct_option_id"],
            )
            flash("Question updated successfully.", "success")
            return redirect(url_for("quiz.manage_questions", quiz_id=question["quiz_id"]))
        except mysql.connector.Error:
            flash("Question could not be updated because the database is unavailable.", "danger")

    return render_template("quiz/question_form.html", quiz=quiz, question=question, mode="edit")


@quiz_bp.route("/admin/questions/<int:question_id>/delete", methods=["POST"])
@role_required("admin")
def delete_question_view(question_id):
    """Delete a question."""

    question = get_question_with_options(question_id)
    if not question:
        flash("Question not found.", "warning")
        return redirect(url_for("quiz.admin_quizzes"))

    quiz_id = question["quiz_id"]

    try:
        delete_question(question_id)
        flash("Question deleted successfully.", "success")
    except mysql.connector.Error:
        flash("Question could not be deleted because it may already have attempt history.", "danger")

    return redirect(url_for("quiz.manage_questions", quiz_id=quiz_id))


@quiz_bp.route("/student/quizzes")
@role_required("student")
def student_quizzes():
    """List quizzes available to students."""

    try:
        quizzes = get_active_quizzes()
    except mysql.connector.Error:
        flash("Quizzes could not be loaded because the database is unavailable.", "danger")
        quizzes = []

    return render_template("quiz/student_quizzes.html", quizzes=quizzes)


@quiz_bp.route("/student/quizzes/<int:quiz_id>/attempt", methods=["GET", "POST"])
@role_required("student")
def attempt_quiz(quiz_id):
    """Show and submit a timed quiz attempt."""

    quiz = get_quiz_by_id(quiz_id)
    if not quiz or quiz["status"] != "active":
        flash("Quiz not found or not available.", "warning")
        return redirect(url_for("quiz.student_quizzes"))

    questions = get_questions_for_quiz(quiz_id)
    if not questions:
        flash("This quiz does not have questions yet.", "warning")
        return redirect(url_for("quiz.student_quizzes"))

    if request.method == "POST":
        submitted_answers = {
            key.replace("question_", ""): value
            for key, value in request.form.items()
            if key.startswith("question_")
        }

        try:
            result_id = submit_quiz_attempt(current_user.user_id, quiz_id, submitted_answers)
            flash("Quiz submitted successfully.", "success")
            return redirect(url_for("quiz.quiz_result", result_id=result_id))
        except mysql.connector.Error:
            flash("Quiz could not be submitted because the database is unavailable.", "danger")

    return render_template("quiz/attempt_quiz.html", quiz=quiz, questions=questions)


@quiz_bp.route("/student/results/<int:result_id>")
@role_required("student")
def quiz_result(result_id):
    """Show a student's quiz result summary."""

    try:
        result_data = get_result_details(result_id, current_user.user_id)
    except mysql.connector.Error:
        flash("Result could not be loaded because the database is unavailable.", "danger")
        result_data = None

    if not result_data:
        flash("Result not found.", "warning")
        return redirect(url_for("dashboard.student_dashboard"))

    return render_template("quiz/quiz_result.html", result=result_data["summary"], answers=result_data["answers"])
