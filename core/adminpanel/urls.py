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
    path("overview/", AdminOverviewView.as_view()),
    path("ai-overview/", AdminAiOverviewView.as_view()),
    path("users/", AdminUsersListView.as_view()),
    path("users/<int:user_id>/", AdminUserDetailView.as_view()),
    path("documents/", AdminDocumentsListView.as_view()),
    path("question-sets/", AdminQuestionSetsListView.as_view()),
    path("attempts/", AdminAttemptsListView.as_view()),
    path("users/<int:user_id>/toggle-active/", AdminToggleUserActiveView.as_view()),
    path("documents/<int:document_id>/delete/", AdminDeleteDocumentView.as_view()),
]