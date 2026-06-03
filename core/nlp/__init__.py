"""
ExamSense+ - NLP Module
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul modulului:
- implementeaza procesarea textului pentru extragerea definitiilor
- detecteaza limba si aplica reguli specifice pentru romana si engleza
- pregateste continutul documentelor pentru generarea intrebarilor

Flow general:
- primeste textul extras din documente
- curata si normalizeaza continutul
- imparte textul in unitati si propozitii relevante
- aplica pattern-uri lingvistice pentru extragerea definitiilor
- filtreaza si ordoneaza rezultatele finale
"""