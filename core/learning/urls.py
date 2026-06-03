"""
ExamSense+ - Learning Routes
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste rutele API pentru modulul de learning
- conecteaza dashboardul de progres, recomandarile si conceptele slabe la view-urile backend
- expune endpoint-ul pentru quiz-ul de recapitulare
"""

from django.urls import path

from .views import (
    LearningDashboardView,
    RecommendationsView,
    RetryQuizView,
    WeakConceptsView,
)


# definim rutele principale pentru modulul de learning
urlpatterns = [
    path("dashboard/", LearningDashboardView.as_view()),
    path("weak-concepts/", WeakConceptsView.as_view()),
    path("recommendations/", RecommendationsView.as_view()),
    path("retry-quiz/", RetryQuizView.as_view()),
]