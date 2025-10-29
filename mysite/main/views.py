from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from quiz.models import *

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'main/index.html')
    
    topics  = Topic.objects.all()
    user_progress = UserTopicProgress.objects.filter(user = request.user)

    not_started = []
    learning = []
    mastered = []

    for topic in topics:
        progress = user_progress.filter(topic=topic).first()

        if not progress:
            not_started.append(topic)
        elif progress.mastery_level == "LEARNING":
            learning.append(topic)
        elif progress.mastery_level == "MASTERED":
            mastered.append(topic)

    return render(request, "main/index.html", {
        "not_started": not_started,
        "learning": learning,
        "mastered": mastered
    })

@login_required
def grades(request):
    queryset = UserTopicProgress.objects.all()
    if request.user.is_authenticated:
        queryset = queryset.filter(user=request.user)
    return render(request, 'main/grades.html', {'progress_list': queryset})