"""
ExamSense+ - Learning Tests
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- verifica dashboardul si functionalitatile din modulul learning
- testeaza conceptele slabe, recomandarile si quiz-ul de recapitulare
- valideaza structura raspunsurilor folosite de frontend

Flow general:
- creeaza date minime pentru un utilizator, un document si un quiz gresit
- apeleaza endpoint-urile de learning
- verifica prezenta statisticilor, conceptelor slabe si intrebarilor de recapitulare
"""

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import (
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuestionSet,
    QuizAnswer,
    QuizAttempt,
)


User = get_user_model()


class LearningApiTests(APITestCase):
    # pregatim date de baza pentru dashboard, recomandari si retry quiz
    def setUp(self):
        self.user = User.objects.create_user(
            username="learnuser",
            email="learnuser@example.com",
            password="ParolaTest123!",
        )

        self.document = Document.objects.create(
            user=self.user,
            file="documents/learning_doc.pdf",
            extracted_text="learning text",
        )

        self.definition = ExtractedDefinition.objects.create(
            document=self.document,
            concept="algoritm",
            definition="o succesiune finita de pasi",
            pattern="este",
            language="ro",
            sentence="Algoritmul este o succesiune finita de pasi.",
            generation_mode="nlp",
        )

        self.question_set = QuestionSet.objects.create(
            document=self.document,
            generation_mode="nlp",
            difficulty="medium",
            max_questions=10,
        )

        self.question = GeneratedQuestion.objects.create(
            document=self.document,
            question_set=self.question_set,
            source_definition=self.definition,
            question_type="mcq",
            generation_mode="nlp",
            language="ro",
            question_text="Ce este algoritmul?",
            options=["o succesiune finita de pasi", "un fisier", "un cablu", "o imprimanta"],
            correct_answer="o succesiune finita de pasi",
        )

        self.attempt = QuizAttempt.objects.create(
            user=self.user,
            document=self.document,
            question_set=self.question_set,
            score=0,
            total_questions=1,
            time_spent_seconds=20,
        )

        QuizAnswer.objects.create(
            attempt=self.attempt,
            question=self.question,
            selected_answer="un fisier",
            is_correct=False,
        )

        self.client.force_authenticate(user=self.user)

    # verificam daca dashboardul returneaza toate sectiunile importante
    def test_learning_dashboard_returns_expected_sections(self):
        response = self.client.get("/api/learning/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("overall", response.data)
        self.assertIn("nlp", response.data)
        self.assertIn("ai", response.data)
        self.assertIn("weak_concepts", response.data)
        self.assertIn("recent_attempts", response.data)

    # verificam daca endpoint-ul de weak concepts returneaza conceptul gresit si definitia lui
    def test_weak_concepts_contains_wrong_concept_and_definition(self):
        response = self.client.get("/api/learning/weak-concepts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["concept"], "algoritm")
        self.assertEqual(response.data["results"][0]["definition"], "o succesiune finita de pasi")

    # verificam daca recomandarile includ atat definitia cat si textul recomandarii
    def test_recommendations_returns_definition_and_recommendation(self):
        response = self.client.get("/api/learning/recommendations/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("definition", response.data["results"][0])
        self.assertIn("recommendation", response.data["results"][0])

    # verificam daca retry quiz genereaza intrebari pentru conceptele slabe
    def test_retry_quiz_returns_questions_for_weak_concepts(self):
        response = self.client.post("/api/learning/retry-quiz/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["questions"][0]["id"], self.question.id)