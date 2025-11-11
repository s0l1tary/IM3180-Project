from .models import *
from django.db.models import Count, Q

weights = {
    "EASY": 1.0,
    "HARD": 2.0
}

def calculate_quiz_score(question_records):
    if not question_records:
        return 0

    total_score = 0
    earned_score = 0

    for q in question_records:
        diff = q["difficulty"]
        is_correct = q["is_correct"]

        total_score += weights[diff]
        if is_correct:
            earned_score += weights[diff]
    
    score = (earned_score / total_score) * 100

    return round(score, 2)


expected_time_difficulty = {
    "EASY": 5,
    "HARD": 10
}

def calculate_time_confidence(time_spent_seconds, easy_count, hard_count, score):
    if score < 40:
        return 1.0  # No bonus if failing
    
    expected_time = (easy_count * expected_time_difficulty["EASY"]) + (hard_count * expected_time_difficulty["HARD"]) 
    
    if time_spent_seconds < 1:
        return 1.0

    time_ratio = time_spent_seconds / expected_time
    
    # Calculate base time multiplier
    if time_ratio <= 0.5:
        bonus = 0.5  # Very fast
    elif time_ratio <= 0.7:
        bonus = 0.3  # Fast
    elif time_ratio <= 1.0:
        bonus = 0.1  # Good pace
    else:
        bonus = 0  # Normal/slow
    
    # Scale bonus by accuracy (40-100% maps to 0-100% of bonus)
    accuracy_scale = (score - 40) / 60
    
    # Final multiplier
    final_multiplier = 1.0 + (bonus * accuracy_scale)
    
    return round(final_multiplier, 2)

def update_user_progress(user_progress, quiz_type, quiz_score, question_records, time_spent=None):
    # Update streaks before calculating score
    user_progress.update_streaks(quiz_score)
    streak_multiplier = user_progress.get_streak_multiplier()

    base_increment = 5
    if quiz_type == 'PLACEMENT':
        updated_score = quiz_score

        # Update recent_score_gain
        user_progress.recent_score_gain = quiz_score
    else:
        # Calculate difficulty factor
        total_weight = sum(weights[q["difficulty"]] for q in question_records)
        difficulty_factor = total_weight/len(question_records)

        # Calculate performance multiplier
        performance_multiplier = 0.4 + 1.6 * (quiz_score / 100)

        # Calculate time confidence
        time_confidence = 1
        if time_spent:
            # Calculate easy and hard questions
            easy_count = sum(1 for q in question_records if q["difficulty"] == "EASY")
            hard_count = sum(1 for q in question_records if q["difficulty"] == "HARD")

            time_confidence = calculate_time_confidence(time_spent, easy_count, hard_count, quiz_score)

        base_score_gain = base_increment * difficulty_factor * performance_multiplier

        total_score_gain = base_score_gain * streak_multiplier * time_confidence

        updated_score = min(100, user_progress.score + total_score_gain)

        # Update recent_score_gain
        if updated_score == 100:
            user_progress.recent_score_gain = 100 - user_progress.score
        else:
            user_progress.recent_score_gain = total_score_gain

    # Update score
    user_progress.score = round(updated_score, 2)

    # Update mastery
    if updated_score == 100:
        user_progress.mastery_level = "MASTERED"
    else:
        user_progress.mastery_level = "LEARNING"

    user_progress.save()

def get_question_mix(user, topic):
    lookback_quizzes = 3

    recent_sessions = QuizSession.objects.filter(
        user = user,
        topic = topic,
        completed_at__isnull = False,
        quiz_type__in = ["REGULAR", "PLACEMENT"],
    ).order_by('-completed_at')[:lookback_quizzes]

    # If no history, return balanced quiz
    if not recent_sessions.exists():
        return 5, 5
    
    # Get all question records from these sessions
    session_ids = recent_sessions.values_list('id', flat=True)
    question_records = QuizQuestionRecord.objects.filter(
        quiz_session_id__in=session_ids
    )
    
    # Calculate accuracy by difficulty
    easy_stats = question_records.filter(difficulty='EASY').aggregate(
        total=Count('id'),
        correct=Count('id', filter=Q(is_correct=True))
    )
    
    hard_stats = question_records.filter(difficulty='HARD').aggregate(
        total=Count('id'),
        correct=Count('id', filter=Q(is_correct=True))
    )
    
    # Calculate accuracy percentages
    easy_accuracy = (easy_stats['correct'] / easy_stats['total'] * 100) if easy_stats['total'] > 0 else 50
    hard_accuracy = (hard_stats['correct'] / hard_stats['total'] * 100) if hard_stats['total'] > 0 else 50
    
    # Adaptive logic based on performance
    if easy_accuracy >= 80 and hard_accuracy >= 60:
        # Mastering both - challenge them with more hard questions
        num_easy, num_hard = 3, 7
    elif easy_accuracy >= 80:
        # Good at easy, struggling with hard - balanced toward hard
        num_easy, num_hard = 4, 6
    elif easy_accuracy >= 60 and hard_accuracy >= 50:
        # Solid performance on both - balanced
        num_easy, num_hard = 5, 5
    elif easy_accuracy >= 60:
        # Decent at easy, poor at hard - slightly more easy
        num_easy, num_hard = 6, 4
    elif hard_accuracy >= 60:
        # Struggling with easy but good at hard (unusual) - focus on easy
        num_easy, num_hard = 7, 3
    else:
        # Struggling overall - focus on fundamentals
        num_easy, num_hard = 7, 3
    
    return num_easy, num_hard


def format_time(seconds): 
    if seconds < 60:
        return f"{int(seconds)}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        if remaining_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {remaining_seconds}s"
    
def get_time_performance(time_spent, easy_count, hard_count):
    expected_time = (easy_count * expected_time_difficulty["EASY"]) + (hard_count * expected_time_difficulty["HARD"]) 
    ratio = time_spent / expected_time
    print(ratio)

    if ratio <= 0.6:
        return {
            'label': 'Lightning Fast',
            'icon': '⚡',
            'class': 'time-excellent'
        }
    elif ratio <= 0.8:
        return {
            'label': 'Fast',
            'icon': '🚀',
            'class': 'time-good'
        }
    elif ratio <= 1.2:
        return {
            'label': 'Steady Pace',
            'icon': '👍',
            'class': 'time-normal'
        }
    elif ratio <= 2.0:
        return {
            'label': 'Careful & Thorough',
            'icon': '🤔',
            'class': 'time-slow'
        }
    else:
        return {
            'label': 'Taking Your Time',
            'icon': '🐢',
            'class': 'time-very-slow'
        }