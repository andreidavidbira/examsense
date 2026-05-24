from django.db.models import Avg, Max, Min, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuizAttempt,
    QuizAnswer
)
from .serializers import (
    ExtractedDefinitionSerializer,
    DocumentListSerializer,
    DocumentDetailSerializer,
    QuizAttemptSerializer,
    SubmitQuizInputSerializer,
    SubmitQuizResponseSerializer,
    QuizStatsResponseSerializer
)
from .utils import extract_text_from_pdf, extract_text_from_docx

from nlp.services import process_text
from quiz.services import generate_questions


class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        filename = file.name.lower()

        if not (filename.endswith(".pdf") or filename.endswith(".docx")):
            return Response({"error": "Unsupported file type"}, status=400)

        document = Document.objects.create(
            user=request.user,
            file=file
        )

        try:
            if filename.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_docx(file)
        except Exception as e:
            return Response({
                "error": "Eroare la extragerea textului",
                "details": str(e)
            }, status=500)

        max_length = 100000
        if len(text) > max_length:
            text = text[:max_length]

        document.extracted_text = text
        document.save()

        try:
            result = process_text(text)
            definitions = result.get("definitions", [])
            definitions_ro = result.get("definitions_ro", [])
            definitions_en = result.get("definitions_en", [])
        except Exception as e:
            return Response({
                "error": "Eroare la procesarea textului",
                "details": str(e)
            }, status=500)

        ExtractedDefinition.objects.filter(document=document).delete()

        saved_definitions = []

        for d in definitions:
            db_definition = ExtractedDefinition.objects.create(
                document=document,
                concept=d.get("concept", ""),
                definition=d.get("definition", ""),
                pattern=d.get("pattern", ""),
                language=d.get("language", ""),
                sentence=d.get("sentence", "")
            )
            saved_definitions.append(db_definition)

        try:
            difficulty = request.data.get("difficulty", "medium")
            max_q = int(request.data.get("max_questions", 10))

            questions = generate_questions(
                definitions,
                difficulty=difficulty,
                max_questions=max_q
            )
        except Exception as e:
            return Response({
                "error": "Eroare la generarea intrebarilor",
                "details": str(e)
            }, status=500)

        GeneratedQuestion.objects.filter(document=document).delete()

        definition_map = {}
        for db_def in saved_definitions:
            key = (db_def.concept, db_def.definition, db_def.language)
            definition_map[key] = db_def

        for q in questions:
            source_definition_obj = None

            if q.get("type") == "mcq":
                for d in definitions:
                    if (
                        d.get("definition") == q.get("correct_answer") and
                        d.get("language") == q.get("language")
                    ):
                        key = (
                            d.get("concept"),
                            d.get("definition"),
                            d.get("language")
                        )
                        source_definition_obj = definition_map.get(key)
                        break

            elif q.get("type") == "mcq_reverse":
                for d in definitions:
                    if (
                        d.get("concept", "").lower() == str(q.get("correct_answer", "")).lower()
                        and d.get("language") == q.get("language")
                    ):
                        key = (
                            d.get("concept"),
                            d.get("definition"),
                            d.get("language")
                        )
                        source_definition_obj = definition_map.get(key)
                        break

            GeneratedQuestion.objects.create(
                document=document,
                source_definition=source_definition_obj,
                question_type=q.get("type"),
                language=q.get("language"),
                question_text=q.get("question"),
                options=q.get("options", None),
                correct_answer=str(q.get("correct_answer"))
            )

        db_definitions = document.definitions.all().order_by("id")
        db_definitions_ro = db_definitions.filter(language="ro")
        db_definitions_en = db_definitions.filter(language="en")

        response_data = {
            "id": document.id,
            "file": document.file.url,
            "uploaded_at": document.uploaded_at,
            "definitions": ExtractedDefinitionSerializer(db_definitions, many=True).data,
            "definitions_ro": ExtractedDefinitionSerializer(db_definitions_ro, many=True).data,
            "definitions_en": ExtractedDefinitionSerializer(db_definitions_en, many=True).data,
            "questions": questions
        }

        if not definitions:
            response_data["warning"] = "Nu s-au putut extrage suficiente definitii relevante din document"

        return Response(response_data)


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        try:
            document = Document.objects.prefetch_related(
                "definitions",
                "generated_questions"
            ).get(id=document_id, user=request.user)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

        serializer = DocumentDetailSerializer(document)
        return Response(serializer.data)


class DeleteDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id, user=request.user)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

        document.delete()
        return Response({"message": "Document deleted successfully"})


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = SubmitQuizInputSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=400)

        document_id = input_serializer.validated_data["document_id"]
        answers = input_serializer.validated_data["answers"]

        try:
            document = Document.objects.get(id=document_id, user=request.user)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

        questions = GeneratedQuestion.objects.filter(document=document)

        if not questions.exists():
            return Response({"error": "No questions found for this document"}, status=404)

        attempt = QuizAttempt.objects.create(
            user=request.user,
            document=document,
            score=0,
            total_questions=questions.count()
        )

        score = 0
        results = []

        question_map = {q.id: q for q in questions}

        for answer_data in answers:
            question_id = answer_data["question_id"]
            selected_answer = answer_data["selected_answer"]

            if question_id not in question_map:
                continue

            question = question_map[question_id]
            correct_answer = question.correct_answer
            is_correct = False

            if question.question_type == "true_false":
                selected_str = str(selected_answer).strip().lower()
                correct_str = str(correct_answer).strip().lower()
                is_correct = selected_str == correct_str
            else:
                is_correct = str(selected_answer).strip() == str(correct_answer).strip()

            if is_correct:
                score += 1

            QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=str(selected_answer),
                is_correct=is_correct
            )

            results.append({
                "question_id": question.id,
                "question": question.question_text,
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

        attempt.score = score
        attempt.total_questions = questions.count()
        attempt.save()

        response_data = {
            "attempt_id": attempt.id,
            "document_id": document.id,
            "score": score,
            "total_questions": attempt.total_questions,
            "results": results
        }

        output_serializer = SubmitQuizResponseSerializer(response_data)
        return Response(output_serializer.data)


class QuizHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user).order_by("-completed_at")
        serializer = QuizAttemptSerializer(attempts, many=True)

        return Response({
            "count": attempts.count(),
            "results": serializer.data
        })


class QuizAttemptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        try:
            attempt = QuizAttempt.objects.prefetch_related("answers__question").get(
                id=attempt_id,
                user=request.user
            )
        except QuizAttempt.DoesNotExist:
            return Response({"error": "Quiz attempt not found"}, status=404)

        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


class QuizStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user)
        answers = QuizAnswer.objects.filter(attempt__user=request.user)

        total_attempts = attempts.count()
        total_answers = answers.count()
        correct_answers = answers.filter(is_correct=True).count()
        wrong_answers = answers.filter(is_correct=False).count()

        avg_score = attempts.aggregate(avg=Avg("score"))["avg"] or 0
        best_score = attempts.aggregate(best=Max("score"))["best"] or 0
        worst_score = attempts.aggregate(worst=Min("score"))["worst"] or 0

        most_wrong_concepts_qs = (
            QuizAnswer.objects
            .filter(attempt__user=request.user, is_correct=False)
            .values("question__source_definition__concept")
            .annotate(wrong_count=Count("id"))
            .order_by("-wrong_count")
        )

        most_wrong_concepts = []

        for item in most_wrong_concepts_qs[:10]:
            concept = item["question__source_definition__concept"]
            if concept:
                most_wrong_concepts.append({
                    "concept": concept,
                    "wrong_count": item["wrong_count"]
                })

        response_data = {
            "total_attempts": total_attempts,
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "average_score": round(avg_score, 2) if avg_score else 0,
            "best_score": best_score,
            "worst_score": worst_score,
            "most_wrong_concepts": most_wrong_concepts
        }

        serializer = QuizStatsResponseSerializer(response_data)
        return Response(serializer.data)