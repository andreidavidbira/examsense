"""
ExamSense+ - Users App Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste configuratia aplicatiei users
- permite identificarea corecta a modulului in proiectul Django
- poate fi extins ulterior pentru initializari specifice autentificarii si utilizatorilor
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    # configuratia de baza pentru aplicatia users
    name = 'users'