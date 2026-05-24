from django.contrib import admin

from .models import (
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuizAttempt,
    QuizAnswer
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file", "uploaded_at")
    search_fields = ("file", "user__username")
    list_filter = ("uploaded_at",)


@admin.register(ExtractedDefinition)
class ExtractedDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "concept", "language", "document", "created_at")
    search_fields = ("concept", "definition", "document__file")
    list_filter = ("language", "created_at")


@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_type", "language", "document", "created_at")
    search_fields = ("question_text", "correct_answer", "document__file")
    list_filter = ("question_type", "language", "created_at")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "document", "score", "total_questions", "completed_at")
    search_fields = ("user__username", "document__file")
    list_filter = ("completed_at",)


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt", "question", "is_correct")
    search_fields = ("selected_answer", "question__question_text")
    list_filter = ("is_correct",)