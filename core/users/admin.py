"""
ExamSense+ - Users Admin Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- inregistreaza modelul custom de utilizator in Django Admin
- permite administrarea conturilor direct din interfata /admin
- configureaza campurile afisate, cautarea si ordonarea utilizatorilor
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# configuram afisarea modelului custom User in Django Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("id",)