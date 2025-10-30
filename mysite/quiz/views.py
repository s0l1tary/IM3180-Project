from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import *
import random
import json
import re
import markdown
from markdown.extensions import Extension
import requests
from django.utils import timezone
from .utils import calculate_quiz_score, update_user_progress, get_question_mix

API_KEY = "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"

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
            if progress.requires_review == True:
                messages.warning(request, "You must review the topic content before attempting a quiz.")
                return redirect("content_pdf", topic_id = topic.id)

            # Create a new quiz session
            quiz = QuizSession.objects.create(user=user, topic=topic, quiz_type="REGULAR")

    # Get 10 questions based on the quiz type and user's score
    if  quiz.quiz_type == "PLACEMENT":
        easy_qs = list(Question.objects.filter(topic=topic, difficulty="EASY").order_by("?")[:5])
        hard_qs = list(Question.objects.filter(topic=topic, difficulty="HARD").order_by("?")[:5])
        questions = easy_qs + hard_qs
    else:
        num_easy, num_hard = get_question_mix(user, topic)

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
    update_user_progress(user_progress, quiz.quiz_type, score, question_records)

    results_url = reverse('results', args=[quiz.id])

    return JsonResponse({
        "message": "Quiz submitted successfully",
        "results_url": results_url,
    })

@login_required
def results(request, quiz_id):
    quiz = QuizSession.objects.get(id=quiz_id)

    # Get question records
    question_records = (
        quiz.question_records
            .all()
            .select_related('question', 'chosen_option')
            .prefetch_related('question__options')
            .order_by('id')
    )

    # Get progress info
    progress = UserTopicProgress.objects.filter(
        user=request.user,
        topic=quiz.topic
    ).first()

    # Calculate old_score
    old_score = progress.score - progress.recent_score_gain
    old_score = max(0, old_score)

    # Calculate statistics
    total_questions = question_records.count()
    correct_answers = question_records.filter(is_correct=True).count()
    easy_correct = question_records.filter(difficulty='EASY', is_correct=True).count()
    easy_total = question_records.filter(difficulty='EASY').count()
    hard_correct = question_records.filter(difficulty='HARD', is_correct=True).count()
    hard_total = question_records.filter(difficulty='HARD').count()

    context = {
        'quiz_session': quiz,
        'question_records': question_records,
        'passed': quiz.score >= 40,
        'topic': quiz.topic,
        'progress': progress,
        'recent_score_gain': progress.recent_score_gain,
        'old_score': old_score,
        
        # Statistics
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'easy_correct': easy_correct,
        'easy_total': easy_total,
        'hard_correct': hard_correct,
        'hard_total': hard_total,
        
        # Streak info
        'pass_streak': progress.pass_streak if progress else None,
        'high_score_streak': progress.high_score_streak if progress else None,
        'fail_streak': progress.fail_streak if progress else 0,
        'requires_review': progress.requires_review if progress else False,
    }

    return render(request, "quiz/results.html", context)

@login_required
def completed(request):
    return render(request, "quiz/completed.html")

@login_required
def explain(request):
    if request.method == "POST":
        question = request.POST.get("question")
        answer = request.POST.get("answer")

        if not question or not answer:
            return JsonResponse({"error": "Missing question or answer."}, status=400)
        
        prompt = f"""
        Explain why this is the correct answer.
        If using mathematical expressions, format them in LaTeX and wrap them in \\( ... \\) for inline math
        or \\[ ... \\] for block math.
        Question: {question}
        Answer: {answer}"""

        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            explanation = data["choices"][0]["message"]["content"]
            explanation = ensure_math_delimiters(explanation)

            # 🔹 Send raw string without escaping backslashes
            return HttpResponse(
                json.dumps({"explanation": explanation}, ensure_ascii=False),
                content_type="application/json"
            )
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "Invalid request method."}, status=405)


def ensure_math_delimiters(text: str) -> str:
    """
    Detects math expressions like \frac, \cos, \pi, etc., and ensures they are
    wrapped in $...$ or \( ... \) so MathJax can render them properly.
    """
    # If text already contains delimiters, don't touch it
    if re.search(r'(\$|\\\(|\\\[)', text):
        return text

    # If plain LaTeX commands are detected but no delimiters
    if re.search(r'\\[a-zA-Z]+', text):
        # Add inline delimiters
        return f"$${text}$$"

    return text