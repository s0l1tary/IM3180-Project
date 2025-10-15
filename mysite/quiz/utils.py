def calculate_quiz_score(question_records):
    if not question_records:
        return 0
    
    difficulty_weights = {
        "EASY": {"correct": 1.0, "wrong": -2.0},
        "HARD": {"correct": 3.0, "wrong": -1.0},
    }
    total_points = 0
    earned_points = 0

    for record in question_records:
        difficulty = record["difficulty"]
        is_correct = record["is_correct"]

        total_points += difficulty_weights[difficulty]["correct"]
        earned_points += difficulty_weights[difficulty]["correct"] if is_correct else difficulty_weights[difficulty]["wrong"]
    
    normalized_score = max(0, min(100, (earned_points/total_points) * 100))
    return round(normalized_score, 1)

def update_user_progress(user_progress, quiz_score):
    old_score = user_progress.score
    updated_score = (0.4 * old_score) + (0.6 * quiz_score)
    user_progress.score = round(updated_score, 1)

    if updated_score >= 85:
        user_progress.mastery_level = "MASTERED"
    else:
        user_progress.mastery_level = "LEARNING"

    user_progress.save()