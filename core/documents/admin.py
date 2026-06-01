from django.contrib import admin

from .models import (
    AIQuizAnswer,
    AIQuizAttempt,
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuestionSet,
    QuizAnswer,
    QuizAttempt,
)


# aici inregistram modelele din documents pentru django admin
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file", "uploaded_at")
    search_fields = ("file", "user__username")
    list_filter = ("uploaded_at",)


@admin.register(ExtractedDefinition)
class ExtractedDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "concept", "language", "generation_mode", "document", "created_at")
    search_fields = ("concept", "definition", "document__file")
    list_filter = ("language", "generation_mode", "created_at")


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "generation_mode", "difficulty", "max_questions", "created_at")
    search_fields = ("document__file", "document__user__username")
    list_filter = ("generation_mode", "difficulty", "created_at")


@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question_set",
        "generation_mode",
        "question_type",
        "language",
        "document",
        "created_at",
    )
    search_fields = ("question_text", "correct_answer", "document__file")
    list_filter = ("generation_mode", "question_type", "language", "created_at")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "document",
        "question_set",
        "score",
        "total_questions",
        "completed_at",
    )
    search_fields = ("user__username", "document__file")
    list_filter = ("completed_at", "question_set__generation_mode")


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt", "question", "is_correct")
    search_fields = ("selected_answer", "question__question_text")
    list_filter = ("is_correct",)


@admin.register(AIQuizAttempt)
class AIQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz_attempt", "model_name", "score", "total_questions", "completed_at")
    search_fields = ("quiz_attempt__user__username", "model_name")
    list_filter = ("completed_at",)


@admin.register(AIQuizAnswer)
class AIQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "ai_attempt", "question", "is_correct")
    search_fields = ("selected_answer", "question__question_text")
    list_filter = ("is_correct",)