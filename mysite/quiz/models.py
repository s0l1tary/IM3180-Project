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
    pdf_file = models.FileField(upload_to='topic_pdfs/', blank=True, null=True)

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
    score = models.FloatField(default=0.0)
    mastery_level = models.CharField(max_length=20, choices=MASTERY_LEVELS, default="LEARNING")
    last_updated = models.DateTimeField(auto_now=True)

    # Failure tracking
    fail_streak = models.IntegerField(default = 0)
    requires_review = models.BooleanField(default = False)

    # Success tracking
    pass_streak = models.IntegerField(default = 0)
    high_score_streak = models.IntegerField(default = 0)

    # Recent score gain
    recent_score_gain = models.FloatField(default = 0.0)

    # Thresholds
    PASS_THRESHOLD = 40.0
    HIGH_SCORE_THRESHOLD = 75.0

    def update_streaks(self, quiz_score):
        if quiz_score < self.PASS_THRESHOLD:
            # Failed
            self.fail_streak += 1
            self.pass_streak = 0
            self.high_score_streak = 0
            
            if self.fail_streak >= 2:
                self.requires_review = True
        else:
            # Passed
            self.fail_streak = 0
            self.requires_review = False
            self.pass_streak += 1
            
            # Check for high score
            if quiz_score >= self.HIGH_SCORE_THRESHOLD:
                self.high_score_streak += 1
            else:
                self.high_score_streak = 0

        self.save()

    def get_streak_multiplier(self):
        multiplier = 1.0

        if self.pass_streak >= 10:
            multiplier += 0.25
        elif self.pass_streak >= 7:
            multiplier += 0.20
        elif self.pass_streak >= 5:
            multiplier += 0.15
        elif self.pass_streak >= 3:
            multiplier += 0.10
        elif self.pass_streak >= 2:
            multiplier += 0.05
        
        # High score streak bonus (max +25%)
        if self.high_score_streak >= 5:
            multiplier += 0.25
        elif self.high_score_streak >= 3:
            multiplier += 0.20
        elif self.high_score_streak >= 2:
            multiplier += 0.10

        return min(1.5, multiplier)

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