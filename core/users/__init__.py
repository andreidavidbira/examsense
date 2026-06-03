"""
ExamSense+ - Users Module
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul modulului:
- gestioneaza autentificarea si conturile utilizatorilor
- implementeaza modelul custom de utilizator
- controleaza login-ul, logout-ul, profilul si resetarea parolei

Flow general:
- utilizatorul isi creeaza cont sau se autentifica in aplicatie
- tokenurile JWT sunt gestionate prin cookie-uri securizate
- utilizatorul isi poate actualiza profilul sau parola
- sistemul valideaza cererile sensibile si aplica rate limiting
- datele utilizatorului sunt folosite de restul modulelor din platforma
"""