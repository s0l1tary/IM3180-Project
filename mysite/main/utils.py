from quiz.models import *

def get_topic(user):
    completed = False
    topic = None
    is_new_topic = False
    score = 0

    # Check if user already has progress
    user_progress = UserTopicProgress.objects.filter(user=user)

    if not user_progress.exists():
        # First-time user → assign Topic 1
        topic = Topic.objects.order_by("id").first()  # first topic in DB
        is_new_topic = True
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
                completed = True
            else:
                topic = next_topic
                is_new_topic = True
        else:
            topic = progress.topic
    
    return {
        "topic": topic,
        "completed": completed,
        "is_new_topic": is_new_topic
    }