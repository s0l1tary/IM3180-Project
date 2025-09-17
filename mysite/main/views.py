from django.shortcuts import render
from django.http import HttpResponse
from .models import Question
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'main/index.html')

@login_required
def home(request):
    return render(request, 'main/home.html')

@login_required
def content(request):
    return render(request, 'main/content.html')

@login_required
def grades(request):
    return render(request, 'main/grades.html')

@login_required
def practice(request):
    return render(request, 'main/practice.html')

@login_required
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

