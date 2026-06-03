"""
ExamSense+ - Users Routes
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste rutele API pentru autentificare si gestionarea contului
- conecteaza endpoint-urile de login, register, logout si refresh la view-urile backend
- expune operatiile pentru profil, schimbare parola si resetare parola
"""

from django.urls import path

from .views import (
    ChangePasswordView,
    CsrfCookieView,
    ForgotPasswordRequestView,
    LoginView,
    LogoutView,
    MeView,
    RefreshCookieTokenView,
    RegisterView,
    ResetPasswordView,
    UpdateProfileView,
)


# definim rutele principale pentru autentificare si cont
urlpatterns = [
    path("csrf/", CsrfCookieView.as_view()),
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshCookieTokenView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path("profile/", UpdateProfileView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
    path("forgot-password/", ForgotPasswordRequestView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
]