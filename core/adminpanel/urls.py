"""
ExamSense+ - Admin Panel Routes
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste rutele API pentru panoul de administrare
- face legatura dintre endpoint-urile adminpanel si view-urile corespunzatoare
- expune statistici globale, liste administrative si actiuni de management pentru utilizatori si documente
"""

from django.urls import path

from .views import (
    AdminAiOverviewView,
    AdminAttemptsListView,
    AdminDeleteDocumentView,
    AdminDocumentsListView,
    AdminOverviewView,
    AdminQuestionSetsListView,
    AdminToggleUserActiveView,
    AdminUserDetailView,
    AdminUsersListView,
)

urlpatterns = [
    # statistici generale pentru dashboardul principal din admin
    path("overview/", AdminOverviewView.as_view()),

    # statistici globale pentru performanta solverului AI
    path("ai-overview/", AdminAiOverviewView.as_view()),

    # lista tuturor utilizatorilor din platforma
    path("users/", AdminUsersListView.as_view()),

    # dashboardul detaliat pentru un utilizator selectat
    path("users/<int:user_id>/", AdminUserDetailView.as_view()),

    # lista tuturor documentelor incarcate in platforma
    path("documents/", AdminDocumentsListView.as_view()),

    # lista tuturor seturilor de intrebari generate
    path("question-sets/", AdminQuestionSetsListView.as_view()),

    # istoricul global al attempturilor de quiz
    path("attempts/", AdminAttemptsListView.as_view()),

    # activare sau dezactivare pentru un utilizator
    path("users/<int:user_id>/toggle-active/", AdminToggleUserActiveView.as_view()),

    # stergerea unui document din panoul de administrare
    path("documents/<int:document_id>/delete/", AdminDeleteDocumentView.as_view()),
]