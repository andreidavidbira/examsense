"""
ExamSense+ - Documents App Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste configuratia aplicatiei documents
- permite identificarea app-ului in cadrul proiectului Django
- poate fi extins ulterior pentru initializari specifice modulului de documente
"""

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    # configuratia de baza pentru aplicatia documents
    name = 'documents'