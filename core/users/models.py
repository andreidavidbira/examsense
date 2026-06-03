"""
ExamSense+ - Users Model
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste modelul custom de utilizator folosit in proiect
- extinde modelul standard AbstractUser din Django
- impune unicitatea adresei de email pentru fiecare cont
- reprezinta baza pentru autentificare, profil si administrarea utilizatorilor
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


# modelul custom de utilizator folosit in intreaga aplicatie
class User(AbstractUser):
    email = models.EmailField(unique=True)

    # afisam username-ul ca reprezentare text a utilizatorului
    def __str__(self):
        return self.username