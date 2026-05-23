from django.db import models
from django.conf import settings


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/")
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.id} - {self.file.name}"


class ExtractedDefinition(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="definitions"
    )
    concept = models.CharField(max_length=255)
    definition = models.TextField()
    pattern = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=10)
    sentence = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.concept} ({self.language})"


class GeneratedQuestion(models.Model):
    QUESTION_TYPES = [
        ("mcq", "Multiple Choice"),
        ("true_false", "True/False"),
        ("mcq_reverse", "Reverse MCQ"),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="generated_questions"
    )
    source_definition = models.ForeignKey(
        ExtractedDefinition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions"
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    language = models.CharField(max_length=10)
    question_text = models.TextField()
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:80]


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt {self.id} - {self.user} - {self.document.id}"


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        GeneratedQuestion,
        on_delete=models.CASCADE,
        related_name="user_answers"
    )
    selected_answer = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer {self.id} - Attempt {self.attempt.id}"