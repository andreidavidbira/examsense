from django.urls import path

from .views import (
    DeleteDocumentView,
    DocumentDetailView,
    DocumentListView,
    QuizAttemptDetailView,
    QuizHistoryView,
    QuizStatsView,
    RegenerateQuestionsView,
    SubmitQuizView,
    UploadDocumentView,
)


# aici definim toate rutele pentru documente, quiz-uri si istoric
urlpatterns = [
    path("", DocumentListView.as_view()),
    path("upload/", UploadDocumentView.as_view()),
    path("submit-quiz/", SubmitQuizView.as_view()),
    path("quiz-history/", QuizHistoryView.as_view()),
    path("quiz-history/<int:attempt_id>/", QuizAttemptDetailView.as_view()),
    path("quiz-stats/", QuizStatsView.as_view()),
    path("<int:document_id>/", DocumentDetailView.as_view()),
    path("<int:document_id>/delete/", DeleteDocumentView.as_view()),
    path("<int:document_id>/regenerate-questions/", RegenerateQuestionsView.as_view()),
]