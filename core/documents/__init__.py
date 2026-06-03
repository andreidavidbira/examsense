"""
ExamSense+ - Documents Module
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul modulului:
- gestioneaza documentele incarcate de utilizatori
- extrage si salveaza textul din fisiere PDF si DOCX
- coordoneaza generarea definitiilor si a intrebarilor de quiz

Flow general:
- utilizatorul incarca un document in aplicatie
- textul este extras si curatat pentru procesare
- documentul este trimis prin fluxul NLP sau AI
- se salveaza definitiile, question set-urile si intrebarile generate
- utilizatorul poate rezolva quiz-uri, vedea istoricul si analiza rezultatele
"""