"""
ExamSense+ - Quiz Module
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul modulului:
- genereaza intrebarile de quiz pe baza definitiilor extrase
- construieste variante de intrebari pentru romana si engleza
- adapteaza tipul intrebarilor in functie de dificultate

Flow general:
- primeste definitiile validate din fluxul NLP sau AI
- analizeaza intentia fiecarei definitii
- genereaza intrebari de tip mcq, true_false sau mcq_reverse
- alege distractori si variante de formulare potrivite
- returneaza setul final de intrebari folosit in aplicatie
"""