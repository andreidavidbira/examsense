from django.conf import settings
from django.db import models


class Document(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    file = models.FileField(upload_to="documents/")
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.id} - {self.file.name}"


class ExtractedDefinition(models.Model):
    GENERATION_MODES = [
        ("nlp", "NLP"),
        ("ai", "AI"),
    ]

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
    generation_mode = models.CharField(
        max_length=10,
        choices=GENERATION_MODES,
        default="nlp",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.concept} ({self.language}) - {self.generation_mode}"


class QuestionSet(models.Model):
    GENERATION_MODES = [
        ("nlp", "NLP"),
        ("ai", "AI"),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="question_sets"
    )
    generation_mode = models.CharField(
        max_length=10,
        choices=GENERATION_MODES,
    )
    difficulty = models.CharField(max_length=20, default="medium")
    max_questions = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QuestionSet {self.id} - Doc {self.document_id} - {self.generation_mode}"


class GeneratedQuestion(models.Model):
    QUESTION_TYPES = [
        ("mcq", "Multiple Choice"),
        ("true_false", "True/False"),
        ("mcq_reverse", "Reverse MCQ"),
    ]

    GENERATION_MODES = [
        ("nlp", "NLP"),
        ("ai", "AI"),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="generated_questions"
    )
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True
    )
    source_definition = models.ForeignKey(
        ExtractedDefinition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions"
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    generation_mode = models.CharField(
        max_length=10,
        choices=GENERATION_MODES,
        default="nlp",
    )
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
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="user_attempts",
        null=True,
        blank=True
    )
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt {self.id} - {self.user} - QS {self.question_set_id}"


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


class AIQuizAttempt(models.Model):
    quiz_attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="ai_attempt"
    )
    model_name = models.CharField(max_length=100, default="")
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Attempt {self.id} - QuizAttempt {self.quiz_attempt_id}"


class AIQuizAnswer(models.Model):
    ai_attempt = models.ForeignKey(
        AIQuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        GeneratedQuestion,
        on_delete=models.CASCADE,
        related_name="ai_answers"
    )
    selected_answer = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"AI Answer {self.id} - AI Attempt {self.ai_attempt_id}"