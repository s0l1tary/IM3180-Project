from django.db import models

class UserTopicProgress(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    topic = models.ForeignKey('quiz.Topic', on_delete=models.CASCADE)  # Adjust app/model as needed
    score = models.FloatField(default=0.0)
    mastery_level = models.CharField(max_length=50, default='Learning')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} ({self.score})"