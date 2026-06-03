"""
ExamSense+ - Documents Routes
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste rutele API pentru modulul de documente si quiz-uri
- face legatura dintre endpoint-urile folosite in frontend si view-urile din backend
- expune functionalitati precum upload document, generare quiz, submit quiz, istoric si statistici
"""

from django.urls import path

from .views import (
    DeleteDocumentView,
    DocumentDetailView,
    DocumentListView,
    QuestionSetDetailView,
    QuizAttemptDetailView,
    QuizHistoryView,
    QuizStatsView,
    RegenerateQuestionsView,
    SubmitQuizView,
    UploadDocumentView,
)

urlpatterns = [
    # lista documentelor utilizatorului autentificat
    path("", DocumentListView.as_view()),

    # upload si procesare pentru un document nou
    path("upload/", UploadDocumentView.as_view()),

    # trimiterea raspunsurilor pentru un quiz
    path("submit-quiz/", SubmitQuizView.as_view()),

    # istoricul quiz-urilor rezolvate de utilizator
    path("quiz-history/", QuizHistoryView.as_view()),

    # detaliile unui attempt din istoric
    path("quiz-history/<int:attempt_id>/", QuizAttemptDetailView.as_view()),

    # statistici generale pentru partea de quiz
    path("quiz-stats/", QuizStatsView.as_view()),

    # detaliile unui question set si intrebarile asociate
    path("question-sets/<int:question_set_id>/quiz/", QuestionSetDetailView.as_view()),

    # detaliile complete ale unui document
    path("<int:document_id>/", DocumentDetailView.as_view()),

    # stergerea unui document al utilizatorului
    path("<int:document_id>/delete/", DeleteDocumentView.as_view()),

    # generarea unui nou set de intrebari pentru un document existent
    path("<int:document_id>/regenerate-questions/", RegenerateQuestionsView.as_view()),
]