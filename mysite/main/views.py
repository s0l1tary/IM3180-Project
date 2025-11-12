from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from quiz.models import *
from .utils import get_topic

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'main/index.html')
    
    score = 0
    topics  = Topic.objects.all()
    user_progress = UserTopicProgress.objects.filter(user = request.user)

    not_started = []
    learning = []
    mastered = []

    # Get topics mastery
    for topic in topics:
        progress = user_progress.filter(topic=topic).first()

        if not progress:
            not_started.append(topic)
        elif progress.mastery_level == "LEARNING":
            learning.append(topic)
            score = progress.score
        elif progress.mastery_level == "MASTERED":
            mastered.append(topic)
    
    topic_info = get_topic(request.user)

    return render(request, "main/index.html", {
        "not_started": not_started,
        "learning": learning,
        "mastered": mastered,
        "topic": topic_info["topic"],
        "completed": topic_info["completed"],
        "is_new_topic": topic_info["is_new_topic"],
        "score": score
    })

@login_required
def grades(request):

    # Get all quiz sessions
    quiz_sessions = QuizSession.objects.select_related('topic').filter(user = request.user)

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

    return render(request, 'main/grades.html', context)