"""
ExamSense+ - Documents Tests
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- verifica flow-urile principale din modulul documents
- testeaza listarea si accesul la documente
- testeaza submit-ul de quiz si izolarea datelor intre utilizatori
- foloseste mock pentru solverul AI, astfel incat testele sa nu depinda de OpenAI

Flow general:
- creeaza utilizatori, documente, question set-uri si intrebari de test
- trimite request-uri catre endpoint-urile documentelor
- verifica permisiunile, validarea si structura raspunsurilor
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document, GeneratedQuestion, QuestionSet


User = get_user_model()


class DocumentsApiTests(APITestCase):
    # pregatim doi utilizatori pentru a verifica izolarea datelor
    def setUp(self):
        self.user = User.objects.create_user(
            username="docuser",
            email="docuser@example.com",
            password="ParolaTest123!",
        )
        self.other_user = User.objects.create_user(
            username="otherdocuser",
            email="otherdocuser@example.com",
            password="ParolaTest123!",
        )

    # verificam daca lista documentelor contine doar documentele userului curent
    def test_document_list_returns_only_current_user_documents(self):
        Document.objects.create(user=self.user, file="documents/user_doc.pdf", extracted_text="abc")
        Document.objects.create(user=self.other_user, file="documents/other_doc.pdf", extracted_text="xyz")

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/documents/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # verificam daca un user nu poate accesa documentul altui user
    def test_document_detail_is_not_accessible_for_other_user_document(self):
        document = Document.objects.create(
            user=self.other_user,
            file="documents/private_doc.pdf",
            extracted_text="private text",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/documents/{document.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # verificam daca submit-ul fara campurile necesare este respins corect
    def test_submit_quiz_invalid_payload_returns_400(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/documents/submit-quiz/",
            {"question_set_id": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("answers", response.data)

    # folosim mock pentru solverul AI astfel incat testul sa nu apeleze OpenAI real
    @patch("documents.views.solve_quiz_with_ai", return_value=[])
    def test_submit_quiz_success_returns_score_and_ai_fields(self, mocked_ai_solver):
        document = Document.objects.create(
            user=self.user,
            file="documents/test_doc.pdf",
            extracted_text="test content",
        )

        question_set = QuestionSet.objects.create(
            document=document,
            generation_mode="nlp",
            difficulty="medium",
            max_questions=10,
        )

        question = GeneratedQuestion.objects.create(
            document=document,
            question_set=question_set,
            question_type="mcq",
            generation_mode="nlp",
            language="ro",
            question_text="Ce este un algoritm?",
            options=["Def 1", "Def 2", "Def 3", "Def 4"],
            correct_answer="Def 1",
        )

        self.client.force_authenticate(user=self.user)

        payload = {
            "question_set_id": question_set.id,
            "elapsed_seconds": 45,
            "answers": [
                {
                    "question_id": question.id,
                    "selected_answer": "Def 1",
                }
            ],
        }

        response = self.client.post("/api/documents/submit-quiz/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 1)
        self.assertEqual(response.data["total_questions"], 1)
        self.assertIn("ai_score", response.data)
        self.assertIn("results", response.data)

    # verificam daca un question set apartinand altui user nu poate fi accesat
    def test_question_set_detail_is_blocked_for_other_user(self):
        document = Document.objects.create(
            user=self.other_user,
            file="documents/other_private.pdf",
            extracted_text="private",
        )

        question_set = QuestionSet.objects.create(
            document=document,
            generation_mode="nlp",
            difficulty="medium",
            max_questions=5,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/documents/question-sets/{question_set.id}/quiz/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)