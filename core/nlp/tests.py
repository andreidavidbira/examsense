"""
ExamSense+ - NLP Tests
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- verifica functiile simple din pipeline-ul NLP
- testeaza curatarea textului si regulile de baza pentru propozitii
- valideaza utilitarele care stau la baza extractiei definitiilor

Flow general:
- trimite texte scurte catre functiile utilitare
- verifica normalizarea spatiilor, curatarea si validarea propozitiilor
- confirma comportamentul de baza al pipeline-ului NLP
"""

from django.test import SimpleTestCase

from nlp.text_cleaner import clean_text
from nlp.definition_extractor import normalize_spaces, is_heading_like, is_valid_sentence


class NlpUtilityTests(SimpleTestCase):
    # verificam daca textul este curatat corect de simboluri si spatii inutile
    def test_clean_text_removes_extra_spaces_and_symbols(self):
        raw_text = "  Algoritm   este   o metoda.  \n\n  •  Test   text  "
        cleaned = clean_text(raw_text)

        self.assertIn("Algoritm este o metoda.", cleaned)
        self.assertIn("Test text", cleaned)

    # verificam daca spatiile multiple sunt reduse la o singura separare
    def test_normalize_spaces_reduces_multiple_spaces(self):
        value = normalize_spaces("Ana    are   mere")
        self.assertEqual(value, "Ana are mere")

    # verificam daca un heading scurt este recunoscut corect
    def test_is_heading_like_detects_short_heading(self):
        self.assertTrue(is_heading_like("Capitol 1"))

    # verificam daca o propozitie normala de definitie este acceptata
    def test_is_valid_sentence_accepts_normal_definition_sentence(self):
        sentence = "Algoritmul este o succesiune finita de pasi folosita pentru rezolvarea unei probleme."
        self.assertTrue(is_valid_sentence(sentence))