import requests
import re
import markdown
from django.shortcuts import render
from django.http import HttpResponse
from .models import Question
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

API_KEY = "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"

@csrf_exempt  # For production, use CSRF token in AJAX and remove this
def explain(request):
    if request.method == "POST":
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        if not question or not answer:
            return JsonResponse({"error": "Missing question or answer."}, status=400)
        prompt = f"Explain why this is the correct answer:\nQuestion: {question}\nAnswer: {answer}"
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
            explanation = markdown_math_safe(explanation)
            return JsonResponse({"explanation": explanation})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def markdown_math_safe(text):
    # Remove [number][number] references
    text = re.sub(r'(\[\d+\])+', '', text)

    # Replace markdown bold **text** with <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    # Replace headers ## text with <h2>text</h2>
    text = re.sub(r'## (.*)', r'<h2>\1</h2>', text)
    text = re.sub(r'# (.*)', r'<h1>\1</h1>', text)

    # Replace bullet points (- or *) with <ul><li>
    # This is a basic approach
    text = re.sub(r'(?:^|\n)[\*\-]\s+(.*)', r'<li>\1</li>', text)

    # Add <ul> around consecutive <li>'s:
    text = re.sub(r'((<li>.*?</li>\n*)+)', r'<ul>\1</ul>', text)

    # Replace double newline with <br><br> for paragraphs
    text = re.sub(r'\n{2,}', '<br><br>', text)
    # Replace single newline with <br>
    text = text.replace('\n', '<br>')

    return text

def index(request):
    return render(request, 'main/index.html')

def home(request):
    return render(request, 'main/home.html')

def content(request):
    return render(request, 'main/content.html')

def grades(request):
    return render(request, 'main/grades.html')

def practice(request):
    return render(request, 'main/practice.html')

def quiz(request):
    """
    GET (no difficulty): show difficulty picker
    GET (?difficulty=EASY|MEDIUM|HARD): show 5 random questions
    POST: grade answers and show results
    """
    # grade submission
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        qids = request.POST.getlist("qids")  # hidden inputs
        total = len(qids)
        score = 0
        results = []

        for qid in qids:
            q = Question.objects.prefetch_related("options").get(pk=qid)
            # find correct option
            correct = next((o for o in q.options.all() if o.is_correct), None)
            chosen_id = request.POST.get(f"q{qid}")  # selected option id
            is_right = correct and str(correct.id) == str(chosen_id)
            if is_right:
                score += 1
            results.append({
                "question": q,
                "options": list(q.options.all()),
                "chosen_id": chosen_id,
                "correct_id": correct.id if correct else None,
                "is_correct": is_right,
            })

        ctx = {"difficulty": difficulty, "score": score, "total": total, "results": results}
        return render(request, "main/quiz_results.html", ctx)

    # show 5 random questions for a difficulty
    difficulty = request.GET.get("difficulty")
    if difficulty in {"EASY", "MEDIUM", "HARD"}:
        questions = (Question.objects
                     .filter(difficulty=difficulty)
                     .order_by("?")[:5]
                     .prefetch_related("options"))
        ctx = {"difficulty": difficulty, "questions": questions}
        return render(request, "main/quiz.html", ctx)

    # no difficulty picked yet
    return render(request, "main/quiz_pick.html")

