from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ------------------------------
# Topic & Question Bank
# ------------------------------
class Topic(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    DIFFICULTIES = (
        ("EASY", "Easy"),
        ("HARD", "Hard"),
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES, default="EASY")
    explanation = models.TextField(blank=True)

    def clean(self):
        options = self.option_set.all()
        correct_count = sum(o.is_correct for o in options)
        if correct_count != 1:
            raise ValidationError("Each question must have exactly one correct option.")

    def __str__(self):
        return f"[{self.topic.name}/{self.difficulty}] {self.text[:40]}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=400)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option(Question {self.question_id}): {self.text[:30]}"


# ------------------------------
# User Progress
# ------------------------------
class UserTopicProgress(models.Model):
    MASTERY_LEVELS = (
        ("LEARNING", "Learning"),
        ("MASTERED", "Mastered"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="topic_progress")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="user_progress")
    score = models.FloatField(default=0.0)  # 0–100 scale
    mastery_level = models.CharField(max_length=20, choices=MASTERY_LEVELS, default="LEARNING")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "topic")  # each user has one progress record per topic

    def __str__(self):
        return f"{self.user.username} - {self.topic.name}: {self.score:.2f}"


# ------------------------------
# Quizzes & Attempts
# ------------------------------
class QuizSession(models.Model):
    QUIZ_TYPES = (
        ("PLACEMENT", "Placement"),
        ("REGULAR", "Regular"),
        ("REVIEW", "Review"),
        ("MIXED", "Mixed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_sessions")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="quiz_sessions")
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default="REGULAR")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} ({self.quiz_type})"


class QuizQuestionRecord(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name="question_records")
    question = models.ForeignKey(Question, on_delete=models.CASCADE,)
    chosen_option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    # denormalized fields for faster scoring
    difficulty = models.CharField(max_length=10, choices=Question.DIFFICULTIES)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quiz_session} - Q{self.question.id} - {'Correct' if self.is_correct else 'Wrong'}"