"""
ExamSense+ - AI Module
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul modulului:
- gestioneaza integrarea aplicatiei cu serviciile AI
- construieste prompturile folosite pentru generarea si rezolvarea quiz-urilor
- valideaza si normalizeaza raspunsurile primite de la model

Flow general:
- primeste textul documentului sau lista de intrebari din backend
- construieste promptul potrivit pentru generare sau rezolvare
- trimite cererea catre modelul AI configurat
- parseaza si curata raspunsul primit
- returneaza date valide mai departe catre modulul documents
"""