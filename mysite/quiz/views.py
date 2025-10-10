from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
import random
import json
from django.utils import timezone

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
            # If all mastered, unlock the next topic
            last_progress = user_progress.order_by("-topic__id").first()
            next_topic = Topic.objects.filter(id__gt=last_progress.topic.id).order_by("id").first()

            if not next_topic:
                return render(request, "quiz/completed.html")

            progress = UserTopicProgress.objects.create(user=user, topic=next_topic, score=0.0, mastery_level="LEARNING")

        topic = progress.topic

        # Create a new quiz session
        quiz = QuizSession.objects.create(user=user, topic=topic, quiz_type="REGULAR")

    # Get 10 random questions from the chosen topic
    questions = list(Question.objects.filter(topic=topic).order_by("?")[:10])
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
            for opt in q.options.all()  # ← fetch options through related_name
        ],
    }
    for q in questions
]

    # Render quiz page
    return render(request, "quiz/quiz.html", {
    "quiz": quiz,
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

    total_questions = len(answers)
    correct_count = 0

    # Process each question
    for qid, selected_opt_id in answers.items():
        try:
            question = Question.objects.get(id=qid)
            chosen_option = Option.objects.get(id=selected_opt_id)
            is_correct = chosen_option.is_correct
        except (Question.DoesNotExist, Option.DoesNotExist):
            continue

        if is_correct:
            correct_count += 1

        # Record each question attempt
        QuizQuestionRecord.objects.create(
            quiz_session=quiz,
            question=question,
            chosen_option=chosen_option,
            is_correct=is_correct,
            difficulty=question.difficulty,
            topic=question.topic,
        )

    # Calculate score
    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    quiz.score = score
    quiz.completed_at = timezone.now()
    quiz.save()

    # Update UserTopicProgress
    progress, _ = UserTopicProgress.objects.get_or_create(user=user, topic=quiz.topic)
    progress.score = (progress.score + score) / 2  # simple average (or customize)
    if progress.score >= 80:
        progress.mastery_level = "MASTERED"
    progress.save()

    request.session["last_score"] = score

    return JsonResponse({
        "message": "Quiz submitted successfully",
        "score": score,
        "mastery_level": progress.mastery_level,
    })

@login_required
def results(request):
    score = request.session.get("last_score", None)
    return render(request, "quiz/results.html", {
        "score": score
    })

@login_required
def completed(request):
    return render(request, "quiz/completed.html")