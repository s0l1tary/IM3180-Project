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

        # Pull 10 random questions from Topic 1
        questions = list(Question.objects.filter(topic=topic).order_by("?")[:5])
    else:
        # 2. Returning user → find their current topic
        # Pick the topic with the lowest score that is not mastered
        progress = user_progress.filter(mastery_level__in=["NOT_STARTED", "LEARNING"]).order_by("score").first()

        if not progress:
            # If all topics mastered, redirect to dashboard or show completion
            return render(request, "quiz/completed.html")

        topic = progress.topic

        # Create a new quiz session
        quiz = QuizSession.objects.create(user=user, topic=topic, quiz_type="REGULAR")

        # 3. Select questions
        questions = []

        # (A) Pull 8 from current topic
        current_qs = list(Question.objects.filter(topic=topic).order_by("?")[:8])
        questions.extend(current_qs)

        # (B) Pull 2 review questions from mastered topics
        mastered_topics = user_progress.filter(mastery_level="MASTERED")
        if mastered_topics.exists():
            review_topic = random.choice(mastered_topics).topic
            review_qs = list(Question.objects.filter(topic=review_topic).order_by("?")[:2])
            questions.extend(review_qs)

        # Ensure we always have 10 questions
        if len(questions) < 10:
            extra_qs = list(Question.objects.filter(topic=topic).order_by("?")[:(10 - len(questions))])
            questions.extend(extra_qs)

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
    quiz = get_object_or_404(QuizSession, id=quiz_id, user=request.user)

    try:
        data = json.loads(request.body.decode("utf-8"))
        answers = data.get("answers", {})
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    total_correct = 0
    topic_accuracy = {}  # {topic_id: [num_correct, num_total]}

    for question_id, option_id in answers.items():
        try:
            question = Question.objects.get(id=question_id)
            chosen_option = Option.objects.get(id=option_id)
        except (Question.DoesNotExist, Option.DoesNotExist):
            continue

        is_correct = chosen_option.is_correct
        if is_correct:
            total_correct += 1

        # Record answer
        QuizQuestionRecord.objects.create(
            quiz_session=quiz,
            question=question,
            chosen_option=chosen_option,
            is_correct=is_correct,
            difficulty=question.difficulty,
            topic=question.topic,
        )

        # Track topic accuracy
        tid = question.topic.id
        if tid not in topic_accuracy:
            topic_accuracy[tid] = [0, 0]
        topic_accuracy[tid][1] += 1
        if is_correct:
            topic_accuracy[tid][0] += 1

    # Compute score
    quiz.score = (total_correct / max(1, len(answers))) * 100
    quiz.completed_at = timezone.now()
    quiz.save()

    # Update user topic progress
    alpha = 0.5
    beta = 0.7

    for tid, (num_correct, num_total) in topic_accuracy.items():
        accuracy = num_correct / num_total
        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic_id=tid,
            defaults={"score": accuracy * 100, "mastery_level": "LEARNING"},
        )

        if not created:
            if tid == quiz.topic.id:
                new_score = (1 - alpha) * progress.score + alpha * (accuracy * 100)
            else:
                new_score = (1 - beta) * progress.score + beta * (accuracy * 100)

            progress.score = new_score

            if progress.score >= 80:
                progress.mastery_level = "MASTERED"
            elif progress.score > 0:
                progress.mastery_level = "LEARNING"
            else:
                progress.mastery_level = "NOT_STARTED"

            progress.save()

    return JsonResponse({
        "message": "Quiz submitted successfully",
        "score": quiz.score,
        "total_correct": total_correct
    })