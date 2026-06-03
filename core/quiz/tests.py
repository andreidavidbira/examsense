"""
ExamSense+ - Quiz Tests
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- verifica generarea intrebarilor de quiz pe baza definitiilor
- testeaza structura intrebarilor rezultate
- valideaza limitele de baza pentru numar de intrebari si tipuri generate

Flow general:
- construieste un set mic de definitii de test
- ruleaza generatorul de intrebari pe dificultati diferite
- verifica structura si consistenta rezultatului final
"""

from django.test import SimpleTestCase

from quiz.services import generate_questions


class QuizGenerationTests(SimpleTestCase):
    # verificam daca generatorul produce o lista valida de intrebari
    def test_generate_questions_returns_valid_question_list(self):
        definitions = [
            {
                "concept": "algoritm",
                "definition": "o succesiune finita de pasi pentru rezolvarea unei probleme",
                "pattern": "este",
                "language": "ro",
                "sentence": "Algoritmul este o succesiune finita de pasi pentru rezolvarea unei probleme.",
            },
            {
                "concept": "variabila",
                "definition": "o zona de memorie care stocheaza o valoare",
                "pattern": "este",
                "language": "ro",
                "sentence": "Variabila este o zona de memorie care stocheaza o valoare.",
            },
            {
                "concept": "function",
                "definition": "a reusable block of code that performs a task",
                "pattern": "is",
                "language": "en",
                "sentence": "A function is a reusable block of code that performs a task.",
            },
            {
                "concept": "array",
                "definition": "a data structure that stores multiple elements of the same type",
                "pattern": "is",
                "language": "en",
                "sentence": "An array is a data structure that stores multiple elements of the same type.",
            },
        ]

        questions = generate_questions(definitions, difficulty="medium", max_questions=4)

        self.assertTrue(len(questions) > 0)
        self.assertTrue(len(questions) <= 4)

        for question in questions:
            self.assertIn(question["type"], {"mcq", "true_false", "mcq_reverse"})
            self.assertIn(question["language"], {"ro", "en"})
            self.assertTrue(question["question"])

    # verificam daca generatorul respecta limita maxima de intrebari ceruta
    def test_generate_questions_respects_max_questions(self):
        definitions = [
            {
                "concept": "algoritm",
                "definition": "o succesiune finita de pasi pentru rezolvarea unei probleme",
                "pattern": "este",
                "language": "ro",
                "sentence": "Algoritmul este o succesiune finita de pasi pentru rezolvarea unei probleme.",
            },
            {
                "concept": "variabila",
                "definition": "o zona de memorie care stocheaza o valoare",
                "pattern": "este",
                "language": "ro",
                "sentence": "Variabila este o zona de memorie care stocheaza o valoare.",
            },
            {
                "concept": "vector",
                "definition": "o colectie ordonata de elemente de acelasi tip",
                "pattern": "este",
                "language": "ro",
                "sentence": "Vectorul este o colectie ordonata de elemente de acelasi tip.",
            },
        ]

        questions = generate_questions(definitions, difficulty="easy", max_questions=2)
        self.assertLessEqual(len(questions), 2)