"""
ExamSense+ - Admin Panel App Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste configuratia aplicatiei adminpanel
- permite identificarea app-ului in cadrul proiectului Django
- poate fi extins ulterior pentru initializari specifice aplicatiei
"""

from django.apps import AppConfig


class AdminpanelConfig(AppConfig):
    # definim configuratia de baza pentru aplicatia adminpanel
    name = 'adminpanel'