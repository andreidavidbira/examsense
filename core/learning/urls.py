from django.urls import path

from .views import (
    LearningDashboardView,
    WeakConceptsView,
    RecommendationsView,
    RetryQuizView
)

urlpatterns = [
    path("dashboard/", LearningDashboardView.as_view()),
    path("weak-concepts/", WeakConceptsView.as_view()),
    path("recommendations/", RecommendationsView.as_view()),
    path("retry-quiz/", RetryQuizView.as_view()),
]