from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import *
import random
import json
import re
from markdown.extensions import Extension
import requests
from django.utils import timezone
from .utils import *
import os
from dotenv import load_dotenv

load_dotenv()  # Automatically loads .env file from project root

API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
# print(f"Loaded API_KEY: {API_KEY is not None}, API_URL: {API_URL is not None}")

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
        "questions": questions_data,
        "topic": topic
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
    time_spent = quiz.get_time_spent()
    update_user_progress(user_progress, quiz.quiz_type, score, question_records, time_spent)

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

    # Calculate time taken
    time_spent = quiz.get_time_spent()
    time_taken_formatted = format_time(time_spent)
    
    # Calculate time performance
    time_performance = get_time_performance(time_spent, easy_total, hard_total)

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

        # Time spent
        'time_spent': time_spent,
        'time_taken_formatted': time_taken_formatted,
        'time_performance': time_performance,
    }

    return render(request, "quiz/results.html", context)


@login_required
def completed(request):
    return render(request, "quiz/completed.html")

SYSTEM_PROMPT = """
You are an interactive tutor helping a university student understand a quiz question.
You will receive:
- The original question,
- The correct answer,
- The student's chosen (wrong) answer,
- And the conversation so far.

Your task:
1. Break down the reasoning into clear, sequential **substeps** that lead from the student's misconception to the correct answer.
2. For each substep:
   - Start with a level-3 markdown heading in the format:
     #### Step X: <short title or concept>
   - Follow with a concise conceptual explanation in 2-4 sentences.
   - End the substep with a multiple-choice question with 2 to 4 options, formatted exactly as:
       A. Option text
       B. Option text
       C. Option text
       D. Option text
3. When the student selects an option, reply with:
   - Begin your response with **“✅ Correct!”** or **“❌ Not quite.”** (bold these emojis and words).
   - Give a brief 1 to 2 sentence explanation for why that answer is right or wrong.
   - Then, if more substeps remain, continue to the next step using the same “### Step X:” heading format.
4. When all substeps are complete:
   - Start the final message with:
     #### 🧭 Final Explanation
   - Write a short, clear summary explaining:
     - Why the correct answer is correct, and  
     - Why the student's original answer was wrong.
5. Always end the final message with the tag: [END]
6. If you need to include mathematical expressions, use proper LaTeX delimiters:
   - Inline math: \( ... \)
   - Block math: \[ ... \]
7. Maintain this **consistent structure and style** across all responses:
   - Use headings for steps.
   - Use bold for emphasis when necessary.
   - Never use italics.
   - Keep all lists and options properly aligned and spaced.
"""

@login_required
def explain(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"} ,status=405)
    
    try:
        data = json.loads(request.body)

        question = data.get("question")
        correct_answer = data.get("correct_answer")
        user_answer = data.get("user_answer")

        # For subsequent API calls
        conversation = data.get("conversation", [])
        user_response = data.get("user_response", "")

        if not question or not correct_answer or not user_answer:
            return JsonResponse({"error": "Missing question or answer."}, status=400)
        
        # Build conversation payload
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.append({
            "role": "user",
            "content": f"Original question: {question}\nCorrect answer: {correct_answer}\nStudent's answer: {user_answer}"
        })

        # Include previous conversation for context
        if conversation:
            messages.extend(conversation)
        
        # Inlcude user's response
        if user_response:
            messages.append({"role": "user", "content": f"I choose: {user_response}"})

        # Call Perplexity API
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-pro",
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            api_data = response.json()

            explanation = api_data["choices"][0]["message"]["content"]
            explanation = ensure_math_delimiters(explanation)

            # Determine if it’s the final message
            finished = "[END]" in explanation

            # Update conversation with user response for the next API call
            if user_response:
                conversation.append({"role": "user", "content": f"I choose: {user_response}"})

            # Update conversation with latest AI reply
            conversation.append({"role": "assistant", "content": explanation})

            # Send raw string without escaping backslashes
            return JsonResponse({
                "reply": explanation.replace("[END]", "").strip(),
                "conversation": conversation,
                "finished": finished
            })
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"API request failed: {str(e)}"}, status=500)
        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=400)
        except KeyError as e:
            return JsonResponse({"error": f"Missing key in response: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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