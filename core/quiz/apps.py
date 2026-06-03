"""
ExamSense+ - Quiz App Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste configuratia aplicatiei quiz
- permite identificarea corecta a modulului in proiectul Django
- poate fi extins ulterior pentru initializari specifice generarii de intrebari
"""

from django.apps import AppConfig


class QuizConfig(AppConfig):
    # configuratia de baza pentru aplicatia quiz
    name = 'quiz'