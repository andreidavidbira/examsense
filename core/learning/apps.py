"""
ExamSense+ - Learning App Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste configuratia aplicatiei learning
- permite identificarea corecta a app-ului in proiectul Django
- seteaza configuratia implicita pentru campurile auto generate
"""

from django.apps import AppConfig


class LearningConfig(AppConfig):
    # configuratia de baza pentru aplicatia learning
    default_auto_field = "django.db.models.BigAutoField"
    name = "learning"