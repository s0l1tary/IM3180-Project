from django.db import models

class UserTopicProgress(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    topic = models.ForeignKey('quiz.Topic', on_delete=models.CASCADE)  # Adjust app/model as needed
    score = models.FloatField(default=0.0)
    mastery_level = models.CharField(max_length=50, default='Learning')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} ({self.score})"


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    
    def __str__(self):
        return self.name



class QuizSession(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Placement', 'Placement'),
    ]
    
    user = models.CharField(max_length=100)
    topic = models.ForeignKey('quiz.Topic', on_delete=models.CASCADE)  # Adjust app/model as needed
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.user} - {self.topic.name} ({self.quiz_type})"