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
def home(request):
    return render(request, 'main/home.html')

@login_required
def practice(request):
    return render(request, 'main/practice.html')

@login_required
def grades(request):
    queryset = UserTopicProgress.objects.all()

    # Get all quiz sessions
    quiz_sessions = QuizSession.objects.select_related('topic').all()

    # Get unique topics for dropdown
    topics = Topic.objects.all()

    # Filter by topic if selected
    selected_topic_id = request.GET.get('topic')
    selected_topic = None
    
    if selected_topic_id:
        try:
            selected_topic = Topic.objects.get(id=selected_topic_id)
            quiz_sessions = quiz_sessions.filter(topic=selected_topic)
        except Topic.DoesNotExist:
            # If topic doesn't exist, show all sessions
            pass
    

    context = {
        'quiz_sessions': quiz_sessions,
        'topics': topics,
        'selected_topic': selected_topic,
    }
    

    if request.user.is_authenticated:
        queryset = queryset.filter(user=request.user)
    return render(request, 'main/grades.html', context)