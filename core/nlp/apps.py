"""
ExamSense+ - NLP App Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste configuratia aplicatiei nlp
- permite identificarea corecta a modulului in proiectul Django
- poate fi extins ulterior pentru initializari specifice pipeline-ului NLP
"""

from django.apps import AppConfig


class NlpConfig(AppConfig):
    # configuratia de baza pentru aplicatia nlp
    name = 'nlp'