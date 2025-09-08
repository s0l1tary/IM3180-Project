from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Question(models.Model):
    DIFFICULTIES = (("EASY","Easy"),("MEDIUM","Medium"),("HARD","Hard"))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES, default="MEDIUM")
    explanation = models.TextField(blank=True)
    def __str__(self): return f"[{self.topic.name}/{self.difficulty}] {self.text[:40]}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=400)
    is_correct = models.BooleanField(default=False)
    def __str__(self): return f"Option({self.question_id}): {self.text[:30]}"
