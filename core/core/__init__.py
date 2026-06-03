"""
ExamSense+ - Core Module
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul modulului:
- reprezinta nucleul de configurare al proiectului Django
- centralizeaza setarile globale, rutele principale si punctele de intrare ale aplicatiei
- conecteaza toate modulele functionale ale platformei

Flow general:
- initializeaza configuratia generala a proiectului
- incarca setarile aplicatiei si variabilele de mediu
- conecteaza rutele principale ale backend-ului
- expune aplicatia pentru rulare in mod WSGI sau ASGI
- ofera infrastructura de baza pentru functionarea intregului sistem ExamSense+
"""