from django.urls import path

from .views import (
    AdminOverviewView,
    AdminUsersListView,
    AdminDocumentsListView,
    AdminAttemptsListView,
    AdminToggleUserActiveView,
    AdminDeleteDocumentView,
)

# aici definim toate rutele disponibile pentru panoul de admin
urlpatterns = [
    path("overview/", AdminOverviewView.as_view()),
    path("users/", AdminUsersListView.as_view()),
    path("documents/", AdminDocumentsListView.as_view()),
    path("attempts/", AdminAttemptsListView.as_view()),
    path("users/<int:user_id>/toggle-active/", AdminToggleUserActiveView.as_view()),
    path("documents/<int:document_id>/delete/", AdminDeleteDocumentView.as_view()),
]