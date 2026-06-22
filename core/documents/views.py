"""
ExamSense+ - Documents Views
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- implementeaza endpoint-urile API pentru documente, quiz-uri si statistici
- valideaza si proceseaza fisierele incarcate de utilizator
- extrage text din PDF si DOCX
- genereaza definitii si intrebari prin flux NLP sau AI
- gestioneaza submit-ul quiz-urilor si comparatia User vs AI
- expune istoricul si statisticile de invatare ale utilizatorului
"""

import time

from django.conf import settings
from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.services import generate_quiz_bundle_with_ai, solve_quiz_with_ai
from nlp.services import process_text
from quiz.services import generate_questions
from users.throttles import QuizSubmitRateThrottle, UploadRateThrottle

from .models import (
    AIQuizAnswer,
    AIQuizAttempt,
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuestionSet,
    QuizAnswer,
    QuizAttempt,
)
from .serializers import (
    DocumentDetailSerializer,
    DocumentListSerializer,
    ExtractedDefinitionSerializer,
    GeneratedQuestionSerializer,
    QuestionSetSerializer,
    QuizAttemptSerializer,
    QuizStatsResponseSerializer,
    SubmitQuizInputSerializer,
    SubmitQuizResponseSerializer,
)
from .utils import extract_text_from_docx, extract_text_from_pdf


# verifica extensia, content type-ul si dimensiunea fisierului incarcat
def validate_uploaded_file(file):
    allowed_extensions = [".pdf", ".docx"]
    allowed_content_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    filename = file.name.lower()

    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise ValueError("Unsupported file type.")

    if hasattr(file, "content_type") and file.content_type:
        if file.content_type not in allowed_content_types:
            raise ValueError("Invalid file content type.")

    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if file.size > max_size:
        raise ValueError("File is too large.")


# calculeaza indexul documentului in istoricul utilizatorului curent
def get_user_document_number(user, document_id):
    return (
        Document.objects
        .filter(user=user, id__lte=document_id)
        .count()
    )


# calculeaza indexul attemptului in istoricul utilizatorului curent
def get_user_attempt_number(user, attempt_id):
    return (
        QuizAttempt.objects
        .filter(user=user, id__lte=attempt_id)
        .count()
    )


# genereaza si salveaza definitiile NLP doar daca nu exista deja pentru document
def ensure_nlp_definitions(document):
    existing = document.definitions.filter(generation_mode="nlp").exists()

    if existing:
        return list(document.definitions.filter(generation_mode="nlp").order_by("id"))
    
    start_time = time.perf_counter()

    text = document.extracted_text or ""
    result = process_text(text)
    definitions = result.get("definitions", [])

    created = []

    for definition in definitions:
        obj = ExtractedDefinition.objects.create(
            document=document,
            concept=definition.get("concept", ""),
            definition=definition.get("definition", ""),
            pattern=definition.get("pattern", ""),
            language=definition.get("language", ""),
            sentence=definition.get("sentence", ""),
            generation_mode="nlp",
        )
        created.append(obj)
    
    duration = time.perf_counter() - start_time
    print(
        f"[NLP DEFINITION EXTRACTION] document_id={document.id}, "
        f"definitions={len(created)}, duration={duration:.4f}s"
    )

    return created


# salveaza in baza de date definitiile generate de AI pentru documentul curent
def save_ai_definitions(document, definitions):
    saved = []

    for definition in definitions:
        obj = ExtractedDefinition.objects.create(
            document=document,
            concept=definition.get("concept", ""),
            definition=definition.get("definition", ""),
            pattern=definition.get("pattern", "ai_generated"),
            language=definition.get("language", ""),
            sentence=definition.get("sentence", ""),
            generation_mode="ai",
        )
        saved.append(obj)

    return saved


# construieste intrebarile NLP pornind de la definitiile deja salvate pentru document
def build_questions_for_document_nlp(document, question_set, difficulty="medium", max_q=10):
    start_time = time.perf_counter()

    db_definitions = list(
        document.definitions
        .filter(generation_mode="nlp")
        .order_by("id")
    )

    definitions = []

    for definition in db_definitions:
        definitions.append({
            "concept": definition.concept,
            "definition": definition.definition,
            "pattern": definition.pattern,
            "language": definition.language,
            "sentence": definition.sentence,
        })

    questions = generate_questions(
        definitions,
        difficulty=difficulty,
        max_questions=max_q,
    )

    definition_map = {}

    for db_definition in db_definitions:
        key = (
            db_definition.concept,
            db_definition.definition,
            db_definition.language,
        )
        definition_map[key] = db_definition

    saved_questions = []

    for question_data in questions:
        source_definition_obj = None

        # incercam sa legam fiecare intrebare de definitia ei sursa
        if question_data.get("type") == "mcq":
            for definition in definitions:
                if (
                    definition.get("definition") == question_data.get("correct_answer")
                    and definition.get("language") == question_data.get("language")
                ):
                    key = (
                        definition.get("concept"),
                        definition.get("definition"),
                        definition.get("language"),
                    )
                    source_definition_obj = definition_map.get(key)
                    break

        elif question_data.get("type") == "mcq_reverse":
            for definition in definitions:
                if (
                    definition.get("concept", "").lower()
                    == str(question_data.get("correct_answer", "")).lower()
                    and definition.get("language") == question_data.get("language")
                ):
                    key = (
                        definition.get("concept"),
                        definition.get("definition"),
                        definition.get("language"),
                    )
                    source_definition_obj = definition_map.get(key)
                    break

        saved_question = GeneratedQuestion.objects.create(
            document=document,
            question_set=question_set,
            source_definition=source_definition_obj,
            question_type=question_data.get("type"),
            generation_mode="nlp",
            language=question_data.get("language"),
            question_text=question_data.get("question"),
            options=question_data.get("options", None),
            correct_answer=str(question_data.get("correct_answer")),
        )
        saved_questions.append(saved_question)
    
        duration = time.perf_counter() - start_time

        print(
        f"[NLP QUIZ GENERATION] document_id={document.id}, "
        f"difficulty={difficulty}, requested={max_q}, "
        f"definitions={len(definitions)}, generated={len(saved_questions)}, "
        f"duration={duration:.4f}s"
        )  

    return saved_questions


# construieste intrebarile AI pornind direct din continutul documentului
def build_questions_for_document_ai(document, question_set, difficulty="medium", max_q=10):
    text = document.extracted_text or ""

    payload = generate_quiz_bundle_with_ai(
        text=text,
        difficulty=difficulty,
        max_questions=max_q,
    )

    definitions = payload.get("definitions", [])
    questions = payload.get("questions", [])

    saved_definitions = save_ai_definitions(document, definitions)

    definition_map = {}
    for db_definition in saved_definitions:
        key = (
            db_definition.concept.strip().lower(),
            db_definition.language,
        )
        definition_map[key] = db_definition

    saved_questions = []

    for question_data in questions:
        source_definition_obj = None

        if question_data.get("type") == "mcq_reverse":
            concept_key = str(question_data.get("correct_answer", "")).strip().lower()
            language_key = question_data.get("language")
            source_definition_obj = definition_map.get((concept_key, language_key))

        saved_question = GeneratedQuestion.objects.create(
            document=document,
            question_set=question_set,
            source_definition=source_definition_obj,
            question_type=question_data.get("type"),
            generation_mode="ai",
            language=question_data.get("language"),
            question_text=question_data.get("question"),
            options=question_data.get("options", None),
            correct_answer=str(question_data.get("correct_answer")),
        )
        saved_questions.append(saved_question)

    return saved_questions


# creeaza un question set nou si genereaza intrebarile in functie de modul ales
def create_question_set_for_document(document, generation_mode="nlp", difficulty="medium", max_q=10):
    question_set = QuestionSet.objects.create(
        document=document,
        generation_mode=generation_mode,
        difficulty=difficulty,
        max_questions=max_q,
    )

    if generation_mode == "ai":
        saved_questions = build_questions_for_document_ai(
            document=document,
            question_set=question_set,
            difficulty=difficulty,
            max_q=max_q,
        )
    else:
        ensure_nlp_definitions(document)
        saved_questions = build_questions_for_document_nlp(
            document=document,
            question_set=question_set,
            difficulty=difficulty,
            max_q=max_q,
        )

    return question_set, saved_questions


class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UploadRateThrottle]

    # valideaza, proceseaza si salveaza un document nou incarcat de utilizator
    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        try:
            validate_uploaded_file(file)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        filename = file.name.lower()

        if not (filename.endswith(".pdf") or filename.endswith(".docx")):
            return Response({"error": "Unsupported file type"}, status=400)

        generation_mode = request.data.get("generation_mode", "nlp")
        difficulty = request.data.get("difficulty", "medium")
        max_q = int(request.data.get("max_questions", 10))

        # extragem textul inainte sa salvam documentul in baza de date
        try:
            if filename.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_docx(file)
        except Exception as e:
            print("TEXT EXTRACTION ERROR:", repr(e))
            return Response({
                "error": "Eroare la extragerea textului",
                "details": str(e),
            }, status=500)

        max_length = 100000
        if len(text) > max_length:
            text = text[:max_length]

        # readucem fisierul la inceput ca sa poata fi salvat corect
        try:
            file.seek(0)
        except Exception:
            pass

        document = Document.objects.create(
            user=request.user,
            file=file,
            extracted_text=text,
        )

        try:
            ensure_nlp_definitions(document)
        except Exception as e:
            print("NLP PROCESSING ERROR:", repr(e))
            return Response({
                "error": "Eroare la procesarea NLP a textului",
                "details": str(e),
            }, status=500)

        try:
            question_set, saved_questions = create_question_set_for_document(
                document=document,
                generation_mode=generation_mode,
                difficulty=difficulty,
                max_q=max_q,
            )
        except Exception as e:
            print("QUESTION GENERATION ERROR:", repr(e))
            return Response({
                "error": "Eroare la generarea intrebarilor",
                "details": str(e),
            }, status=500)

        document.refresh_from_db()

        response_data = {
            "id": document.id,
            "file": document.file.url,
            "uploaded_at": document.uploaded_at,
            "latest_question_set_id": question_set.id,
            "definitions": ExtractedDefinitionSerializer(
                document.definitions.all().order_by("id"),
                many=True
            ).data,
            "questions": GeneratedQuestionSerializer(saved_questions, many=True).data,
            "question_sets": QuestionSetSerializer(
                document.question_sets.all().order_by("-created_at"),
                many=True
            ).data,
        }

        return Response(response_data)


class RegenerateQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    # genereaza un nou set de intrebari pentru un document existent
    def post(self, request, document_id):
        document = get_object_or_404(
            Document.objects.prefetch_related("definitions"),
            id=document_id,
            user=request.user,
        )

        generation_mode = request.data.get("generation_mode", "nlp")
        difficulty = request.data.get("difficulty", "medium")
        max_q = int(request.data.get("max_questions", 10))

        try:
            question_set, saved_questions = create_question_set_for_document(
                document=document,
                generation_mode=generation_mode,
                difficulty=difficulty,
                max_q=max_q,
            )
        except Exception as e:
            return Response({
                "error": "Nu am putut genera un nou set de intrebari.",
                "details": str(e),
            }, status=500)

        return Response({
            "message": "A fost generat un nou set de intrebari.",
            "document_id": document.id,
            "question_set_id": question_set.id,
            "generation_mode": question_set.generation_mode,
            "user_document_number": get_user_document_number(request.user, document.id),
            "questions": GeneratedQuestionSerializer(saved_questions, many=True).data,
        })


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    # intoarce lista documentelor utilizatorului autentificat
    def get(self, request):
        documents = Document.objects.filter(user=request.user).order_by("-uploaded_at")
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # intoarce toate datele necesare pentru pagina de detalii a unui document
    def get(self, request, document_id):
        document = get_object_or_404(
            Document.objects.prefetch_related(
                "definitions",
                "generated_questions",
                "question_sets",
            ),
            id=document_id,
            user=request.user,
        )

        serializer = DocumentDetailSerializer(document)
        return Response(serializer.data)


class QuestionSetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # intoarce intrebarile si metadatele unui question set
    def get(self, request, question_set_id):
        question_set = get_object_or_404(
            QuestionSet.objects.select_related("document"),
            id=question_set_id,
            document__user=request.user,
        )

        questions = question_set.questions.all().order_by("id")

        return Response({
            "question_set_id": question_set.id,
            "document_id": question_set.document.id,
            "user_document_number": get_user_document_number(request.user, question_set.document.id),
            "generation_mode": question_set.generation_mode,
            "difficulty": question_set.difficulty,
            "max_questions": question_set.max_questions,
            "questions": GeneratedQuestionSerializer(questions, many=True).data,
        })


class DeleteDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    # sterge un document al utilizatorului curent
    def delete(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)
        document.delete()
        return Response({"message": "Document deleted successfully"})


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [QuizSubmitRateThrottle]

    # evalueaza raspunsurile utilizatorului si ruleaza solverul AI pe acelasi quiz
    def post(self, request):
        input_serializer = SubmitQuizInputSerializer(data=request.data)

        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=400)

        question_set_id = input_serializer.validated_data["question_set_id"]
        answers = input_serializer.validated_data["answers"]
        elapsed_seconds = input_serializer.validated_data.get("elapsed_seconds", 0)

        question_set = get_object_or_404(
            QuestionSet.objects.select_related("document"),
            id=question_set_id,
            document__user=request.user,
        )

        document = question_set.document
        questions = question_set.questions.all()

        if not questions.exists():
            return Response({"error": "No questions found for this question set"}, status=404)

        attempt = QuizAttempt.objects.create(
            user=request.user,
            document=document,
            question_set=question_set,
            score=0,
            total_questions=questions.count(),
            time_spent_seconds=max(0, int(elapsed_seconds)),
        )

        score = 0
        results = []

        question_map = {question.id: question for question in questions}

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
                is_correct=is_correct,
            )

            results.append({
                "question_id": question.id,
                "question": question.question_text,
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
            })

        attempt.score = score
        attempt.total_questions = questions.count()
        attempt.save()

        ai_score = 0
        ai_results = []
        ai_model_name = "unavailable"
        ai_time_spent_seconds = 0

        try:
            ai_start = time.perf_counter()
            ai_answers_payload = solve_quiz_with_ai(list(questions))
            ai_elapsed = time.perf_counter() - ai_start
            ai_time_spent_seconds = max(0, round(ai_elapsed))

            ai_attempt = AIQuizAttempt.objects.create(
                quiz_attempt=attempt,
                model_name=settings.OPENAI_SOLVER_MODEL,
                score=0,
                total_questions=questions.count(),
                time_spent_seconds=ai_time_spent_seconds,
            )

            for ai_answer_data in ai_answers_payload:
                question_id = ai_answer_data.get("question_id")
                selected_answer = ai_answer_data.get("selected_answer")

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
                    ai_score += 1

                AIQuizAnswer.objects.create(
                    ai_attempt=ai_attempt,
                    question=question,
                    selected_answer=str(selected_answer),
                    is_correct=is_correct,
                )

                ai_results.append({
                    "question_id": question.id,
                    "question": question.question_text,
                    "ai_selected_answer": selected_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                })

            ai_attempt.score = ai_score
            ai_attempt.total_questions = questions.count()
            ai_attempt.save()
            ai_model_name = settings.OPENAI_SOLVER_MODEL

        except Exception as e:
            print("AI SOLVER ERROR:", repr(e))
            ai_score = 0
            ai_results = []
            ai_model_name = "unavailable"
            ai_time_spent_seconds = 0

        user_document_number = (
            Document.objects
            .filter(user=request.user, id__lte=document.id)
            .count()
        )
        user_attempt_number = (
            QuizAttempt.objects
            .filter(user=request.user, id__lte=attempt.id)
            .count()
        )

        response_data = {
            "attempt_id": attempt.id,
            "question_set_id": question_set.id,
            "generation_mode": question_set.generation_mode,
            "user_attempt_number": user_attempt_number,
            "document_id": document.id,
            "user_document_number": user_document_number,
            "score": score,
            "total_questions": attempt.total_questions,
            "user_time_spent_seconds": attempt.time_spent_seconds,
            "results": results,
            "ai_score": ai_score,
            "ai_total_questions": questions.count(),
            "ai_model_name": ai_model_name,
            "ai_time_spent_seconds": ai_time_spent_seconds,
            "ai_results": ai_results,
        }

        output_serializer = SubmitQuizResponseSerializer(response_data)
        return Response(output_serializer.data)


class QuizHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    # intoarce istoricul quiz-urilor rezolvate de utilizator
    def get(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user).order_by("-completed_at")
        serializer = QuizAttemptSerializer(attempts, many=True)

        return Response({
            "count": attempts.count(),
            "results": serializer.data,
        })


class QuizAttemptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # intoarce detaliile complete pentru un attempt din istoric
    def get(self, request, attempt_id):
        attempt = get_object_or_404(
            QuizAttempt.objects.prefetch_related(
                "answers__question",
                "ai_attempt__answers__question",
            ),
            id=attempt_id,
            user=request.user,
        )

        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


# calculeaza statistici pe overall, nlp si ai pentru dashboardul quiz-urilor
def build_mode_stats(attempts_queryset):
    answers_queryset = QuizAnswer.objects.filter(attempt__in=attempts_queryset)
    ai_attempts_queryset = AIQuizAttempt.objects.filter(quiz_attempt__in=attempts_queryset)

    total_attempts = attempts_queryset.count()
    correct_answers = answers_queryset.filter(is_correct=True).count()
    wrong_answers = answers_queryset.filter(is_correct=False).count()

    average_score = attempts_queryset.aggregate(avg=Avg("score"))["avg"] or 0
    best_score = attempts_queryset.aggregate(best=Max("score"))["best"] or 0
    worst_score = attempts_queryset.aggregate(worst=Min("score"))["worst"] or 0

    ai_average_score = ai_attempts_queryset.aggregate(avg=Avg("score"))["avg"] or 0
    ai_best_score = ai_attempts_queryset.aggregate(best=Max("score"))["best"] or 0

    ai_wins = 0
    user_wins = 0
    ties = 0

    for attempt in attempts_queryset.select_related("ai_attempt"):
        if not hasattr(attempt, "ai_attempt"):
            continue

        if attempt.score > attempt.ai_attempt.score:
            user_wins += 1
        elif attempt.score < attempt.ai_attempt.score:
            ai_wins += 1
        else:
            ties += 1

    return {
        "total_attempts": total_attempts,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "average_score": round(average_score, 2) if average_score else 0,
        "best_score": best_score,
        "worst_score": worst_score,
        "ai_average_score": round(ai_average_score, 2) if ai_average_score else 0,
        "ai_best_score": ai_best_score,
        "ai_wins": ai_wins,
        "user_wins": user_wins,
        "ties": ties,
    }


class QuizStatsView(APIView):
    permission_classes = [IsAuthenticated]

    # intoarce statisticile generale ale utilizatorului pentru dashboardul de quiz
    def get(self, request):
        overall_attempts = QuizAttempt.objects.filter(user=request.user)
        nlp_attempts = overall_attempts.filter(question_set__generation_mode="nlp")
        ai_attempts = overall_attempts.filter(question_set__generation_mode="ai")

        wrong_concepts_qs = (
            QuizAnswer.objects
            .filter(attempt__user=request.user, is_correct=False)
            .values("question__source_definition__concept")
            .annotate(wrong_count=Count("id"))
            .order_by("-wrong_count")
        )

        most_wrong_concepts = []

        for item in wrong_concepts_qs[:10]:
            concept = item["question__source_definition__concept"]

            if concept:
                most_wrong_concepts.append({
                    "concept": concept,
                    "wrong_count": item["wrong_count"],
                })

        response_data = {
            "overall": build_mode_stats(overall_attempts),
            "nlp": build_mode_stats(nlp_attempts),
            "ai": build_mode_stats(ai_attempts),
            "most_wrong_concepts": most_wrong_concepts,
        }

        serializer = QuizStatsResponseSerializer(response_data)
        return Response(serializer.data)