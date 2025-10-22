from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
import random
import json
from django.utils import timezone
from .utils import calculate_quiz_score, update_user_progress

@login_required
def take_quiz(request):
    user = request.user

    # Check if user already has progress
    user_progress = UserTopicProgress.objects.filter(user=user)

    if not user_progress.exists():
        # First-time user → assign Topic 1
        topic = Topic.objects.order_by("id").first()  # first topic in DB
        progress = UserTopicProgress.objects.create(user=user, topic=topic, score=0.0)

        # Create placement quiz
        quiz = QuizSession.objects.create(user=user, topic=topic, quiz_type="PLACEMENT")
    else:
        # 2. Returning user → find their current topic
        # Pick the topic with the lowest score that is not mastered
        progress = user_progress.filter(mastery_level="LEARNING").first()

        if not progress:
            # If all prevous topics are mastered, unlock the next topic
            last_progress = user_progress.order_by("-topic__id").first()
            next_topic = Topic.objects.filter(id__gt=last_progress.topic.id).order_by("id").first()

            # If user mastered all topics, show completed page
            if not next_topic:
                return render(request, "quiz/completed.html")

            progress = UserTopicProgress.objects.create(user=user, topic=next_topic, score=0.0, mastery_level="LEARNING")
            topic = progress.topic

            # Create placement quiz
            quiz = QuizSession.objects.create(user=user, topic=topic, quiz_type="PLACEMENT")
        else:
            topic = progress.topic

            # Create a new quiz session
            quiz = QuizSession.objects.create(user=user, topic=topic, quiz_type="REGULAR")

    # Get 10 questions based on the quiz type and user's score
    if quiz.quiz_type == "PLACEMENT":
        easy_qs = list(Question.objects.filter(topic=topic, difficulty="EASY").order_by("?")[:5])
        hard_qs = list(Question.objects.filter(topic=topic, difficulty="HARD").order_by("?")[:5])
        questions = easy_qs + hard_qs
    else:
        score = progress.score
        if score < 50:
            num_easy, num_hard = 7, 3
        elif score < 80:
            num_easy, num_hard = 5, 5
        else:
            num_easy, num_hard = 3, 7

        easy_qs = list(Question.objects.filter(topic=topic, difficulty="EASY").order_by("?")[:num_easy])
        hard_qs = list(Question.objects.filter(topic=topic, difficulty="HARD").order_by("?")[:num_hard])
        questions = easy_qs + hard_qs

    random.shuffle(questions)  # mix review and current

    # Serialize questions for JSON
    questions_data = [
        {
            "id": q.id,
            "text": q.text,
            "difficulty": q.difficulty,
            "explanation": q.explanation,
            "options": [
                {
                    "id": opt.id,
                    "text": opt.text,
                    "is_correct": opt.is_correct,
                }
                for opt in random.sample(list(q.options.all()), k=q.options.count())  # shuffle options
            ],
        }
        for q in questions
    ]

    # Render quiz page
    return render(request, "quiz/quiz.html", {
        "quiz_id": quiz.id,
        "quiz_type": quiz.quiz_type,
        "questions": questions_data
    })


@login_required
def submit_quiz(request, quiz_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    user = request.user
    try:
        quiz = QuizSession.objects.get(id=quiz_id, user=user)
    except QuizSession.DoesNotExist:
        return JsonResponse({"error": "Quiz not found"}, status=404)

    data = json.loads(request.body)
    answers = data.get("answers", {})

    question_records = []

    # Process each question
    for qid, selected_opt_id in answers.items():
        try:
            question = Question.objects.get(id=qid)
            chosen_option = Option.objects.get(id=selected_opt_id)
            is_correct = chosen_option.is_correct
        except (Question.DoesNotExist, Option.DoesNotExist):
            continue

        # Record each question attempt
        QuizQuestionRecord.objects.create(
            quiz_session=quiz,
            question=question,
            chosen_option=chosen_option,
            is_correct=is_correct,
            difficulty=question.difficulty,
            topic=question.topic,
        )

        question_records.append({
            "difficulty": question.difficulty,
            "is_correct": is_correct
        })

    # Calculate score
    score = calculate_quiz_score(question_records)
    quiz.score = score
    quiz.completed_at = timezone.now()
    quiz.save()

    # Update UserTopicProgress
    user_progress = UserTopicProgress.objects.get(user=user, topic=quiz.topic)
    if quiz.quiz_type == "PLACEMENT":
        user_progress.score = score
        user_progress.save()
    else:
        update_user_progress(user_progress, score)

    request.session["last_score"] = score

    return JsonResponse({
        "message": "Quiz submitted successfully",
        "score": score,
        "mastery_level": user_progress.mastery_level,
    })


# ✅ Edited results() function only
@login_required
def results(request):
    score = request.session.get("last_score", 0)

    # Temporary demo values (replace with real data later)
    total = 100
    correct_count = int(score / 10)     # e.g. each correct = 10 pts
    total_count = 10
    percent = round(score, 0)

    topics = [
        {"name": "LTI Systems", "status": "Competent"},
        {"name": "Fourier Series", "status": "Learning"},
        {"name": "Convolution", "status": "Learning"},
    ]

    return render(request, "quiz/results.html", {
        "score": score,
        "total": total,
        "correct_count": correct_count,
        "total_count": total_count,
        "percent": percent,
        "topics": topics,
    })


@login_required
def completed(request):
    return render(request, "quiz/completed.html")
