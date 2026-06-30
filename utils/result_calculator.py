def get_selected_option_id(raw_selected_option, valid_option_ids):
    """Return a selected option ID only when it belongs to the current question."""

    if not raw_selected_option:
        return None

    try:
        selected_option_id = int(raw_selected_option)
    except ValueError:
        return None

    if selected_option_id not in valid_option_ids:
        return None

    return selected_option_id


def calculate_quiz_result(questions, submitted_answers):
    """Calculate score, accuracy, and per-question correctness."""

    total_questions = len(questions)
    correct_answers = 0
    scored_answers = []

    for question in questions:
        valid_option_ids = [option["option_id"] for option in question["options"]]
        selected_option_id = get_selected_option_id(
            submitted_answers.get(str(question["question_id"])),
            valid_option_ids,
        )
        correct_option_id = None

        for option in question["options"]:
            if option["is_correct"]:
                correct_option_id = option["option_id"]
                break

        is_correct = selected_option_id == correct_option_id
        if is_correct:
            correct_answers += 1

        scored_answers.append(
            {
                "question_id": question["question_id"],
                "selected_option": selected_option_id,
                "is_correct": is_correct,
            }
        )

    incorrect_answers = total_questions - correct_answers
    accuracy = round((correct_answers / total_questions * 100), 2) if total_questions else 0

    return {
        "score": correct_answers,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "total_questions": total_questions,
        "accuracy": accuracy,
        "scored_answers": scored_answers,
    }
