from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from quiz.models import UserTopicProgress, Topic

# Create your views here.
@login_required
def content(request):
    topics = Topic.objects.filter(user_progress__user = request.user)

    learning_topics = topics.filter(user_progress__user=request.user, user_progress__mastery_level="LEARNING")
    mastered_topics = topics.filter(user_progress__user=request.user, user_progress__mastery_level="MASTERED")

    return render(request, 'content/content.html', {
        "learning_topics": learning_topics,
        "mastered_topics": mastered_topics 
    })

@login_required
def content_pdf(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    return render(request, "content/materials.html", {
        'topic': topic
    })