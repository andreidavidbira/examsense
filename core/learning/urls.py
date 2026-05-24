from django.urls import path

from .views import (
    LearningDashboardView,
    RecommendationsView,
    RetryQuizView,
    WeakConceptsView,
)


# aici definim rutele pentru dashboard, recomandari si quiz-ul de recapitulare
urlpatterns = [
    path("dashboard/", LearningDashboardView.as_view()),
    path("weak-concepts/", WeakConceptsView.as_view()),
    path("recommendations/", RecommendationsView.as_view()),
    path("retry-quiz/", RetryQuizView.as_view()),
]