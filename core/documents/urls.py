from django.urls import path
from .views import (
    UploadDocumentView,
    DocumentListView,
    DocumentDetailView,
    DeleteDocumentView,
    SubmitQuizView,
    QuizHistoryView,
    QuizAttemptDetailView,
    QuizStatsView
)

urlpatterns = [
    path("upload/", UploadDocumentView.as_view()),
    path("", DocumentListView.as_view()),
    path("<int:document_id>/", DocumentDetailView.as_view()),
    path("<int:document_id>/delete/", DeleteDocumentView.as_view()),
    path("submit-quiz/", SubmitQuizView.as_view()),
    path("quiz-history/", QuizHistoryView.as_view()),
    path("quiz-history/<int:attempt_id>/", QuizAttemptDetailView.as_view()),
    path("quiz-stats/", QuizStatsView.as_view()),
]