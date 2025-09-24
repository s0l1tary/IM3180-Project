from django.shortcuts import render
from django.http import HttpResponse
from .models import Question, Topic  # <- Topic added


def index(request):
    return render(request, "main/index.html")


def home(request):
    return render(request, "main/home.html")


def content(request):
    return render(request, "main/content.html")


def grades(request):
    return render(request, "main/grades.html")


def practice(request):
    """
    GET without difficulty -> landing header/buttons
    GET ?difficulty=EASY|MEDIUM|HARD -> show 5 random questions (practice view)
    """
    difficulty = request.GET.get("difficulty")

    if difficulty in {"EASY", "MEDIUM", "HARD"}:
        questions = (
            Question.objects
            .filter(difficulty=difficulty)
            .order_by("?")[:5]
            .prefetch_related("options")
        )
        return render(request, "main/practice.html", {
            "difficulty": difficulty,
            "questions": questions,
        })

    # landing state
    return render(request, "main/practice.html", {
        "difficulty": None,
        "questions": [],
    })


def quiz(request):
    """
    GET (no params): show picker with topic list
    GET (?topic=<slug>&difficulty=EASY|MEDIUM|HARD): show 5 random questions
    POST: grade answers and show results (preserve topic & difficulty)
    """
    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        topic_slug = request.POST.get("topic")
        topic = Topic.objects.filter(slug=topic_slug).first() if topic_slug else None

        qids = request.POST.getlist("qids")
        total = len(qids)
        score = 0
        results = []

        for qid in qids:
            q = Question.objects.prefetch_related("options").get(pk=qid)
            correct = next((o for o in q.options.all() if o.is_correct), None)
            chosen_id = request.POST.get(f"q{qid}")
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

        ctx = {
            "topic": topic,
            "difficulty": difficulty,
            "score": score,
            "total": total,
            "results": results,
        }
        return render(request, "main/quiz_results.html", ctx)

    # GET
    difficulty = request.GET.get("difficulty")
    topic_slug = request.GET.get("topic")
    topic = Topic.objects.filter(slug=topic_slug).first() if topic_slug else None

    if difficulty in {"EASY", "MEDIUM", "HARD"}:
        qs = Question.objects.filter(difficulty=difficulty)
        if topic:
            qs = qs.filter(topic=topic)
        questions = qs.order_by("?").prefetch_related("options")[:5]
        return render(request, "main/quiz.html", {
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
        })

    # picker page shows topics + difficulty select
    topics = Topic.objects.order_by("name")
    return render(request, "main/quiz_pick.html", {"topics": topics})



