from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Min

from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import (
    AIQuizAnswer,
    AIQuizAttempt,
    Document,
    ExtractedDefinition,
    GeneratedQuestion,
    QuestionSet,
    QuizAnswer,
    QuizAttempt,
)
from .permissions import IsAdminPanelUser
from .serializers import (
    AdminAiOverviewSerializer,
    AdminAttemptSerializer,
    AdminDocumentSerializer,
    AdminOverviewSerializer,
    AdminQuestionSetSerializer,
    AdminUserDetailSerializer,
    AdminUserSerializer,
    ToggleUserActiveSerializer,
)


User = get_user_model()


# calculeaza numarul documentului raportat doar la utilizatorul curent
def get_user_document_number(user_id, document_id):
    return (
        Document.objects
        .filter(user_id=user_id, id__lte=document_id)
        .count()
    )


# calculeaza numarul attemptului raportat doar la utilizatorul curent
def get_user_attempt_number(user_id, attempt_id):
    return (
        QuizAttempt.objects
        .filter(user_id=user_id, id__lte=attempt_id)
        .count()
    )


# intoarce statisticile de baza pentru un queryset de attempturi ale utilizatorilor
def build_attempt_stats(attempts_qs):
    average_score = attempts_qs.aggregate(avg=Avg("score"))["avg"] or 0
    best_score = attempts_qs.aggregate(best=Max("score"))["best"] or 0
    worst_score = attempts_qs.aggregate(worst=Min("score"))["worst"] or 0

    answers_qs = QuizAnswer.objects.filter(attempt__in=attempts_qs)
    correct_answers = answers_qs.filter(is_correct=True).count()
    wrong_answers = answers_qs.filter(is_correct=False).count()

    return {
        "attempts_count": attempts_qs.count(),
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "average_score": round(average_score, 2) if average_score else 0,
        "best_score": best_score,
        "worst_score": worst_score,
    }


# intoarce statisticile AI pentru un queryset de attempturi AI
def build_ai_attempt_stats(ai_attempts_qs):
    average_score = ai_attempts_qs.aggregate(avg=Avg("score"))["avg"] or 0
    best_score = ai_attempts_qs.aggregate(best=Max("score"))["best"] or 0
    worst_score = ai_attempts_qs.aggregate(worst=Min("score"))["worst"] or 0

    answers_qs = AIQuizAnswer.objects.filter(ai_attempt__in=ai_attempts_qs)
    correct_answers = answers_qs.filter(is_correct=True).count()
    wrong_answers = answers_qs.filter(is_correct=False).count()

    return {
        "attempts_count": ai_attempts_qs.count(),
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "average_score": round(average_score, 2) if average_score else 0,
        "best_score": best_score,
        "worst_score": worst_score,
    }


# construieste comparatia user vs ai pentru un queryset de attempturi
def build_user_vs_ai_stats(attempts_qs):
    ai_attempts_qs = AIQuizAttempt.objects.filter(quiz_attempt__in=attempts_qs)

    compared_count = 0
    user_wins = 0
    ai_wins = 0
    draws = 0

    for ai_attempt in ai_attempts_qs.select_related("quiz_attempt"):
        compared_count += 1
        user_score = ai_attempt.quiz_attempt.score
        ai_score = ai_attempt.score

        if user_score > ai_score:
            user_wins += 1
        elif ai_score > user_score:
            ai_wins += 1
        else:
            draws += 1

    return {
        "compared_attempts": compared_count,
        "user_wins": user_wins,
        "ai_wins": ai_wins,
        "draws": draws,
    }


# intoarce top concepte gresite pentru un utilizator
def build_most_wrong_concepts_for_user(user, limit=10):
    wrong_answers = (
        QuizAnswer.objects
        .filter(attempt__user=user, is_correct=False)
        .values("question__source_definition__concept")
        .annotate(wrong_count=Count("id"))
        .order_by("-wrong_count")
    )

    results = []

    for item in wrong_answers:
        concept = item["question__source_definition__concept"]

        if not concept:
            continue

        results.append({
            "concept": concept,
            "wrong_count": item["wrong_count"],
        })

        if len(results) >= limit:
            break

    return results


# construieste dashboardul complet pentru un user
def build_user_dashboard_data(user):
    all_attempts = QuizAttempt.objects.filter(user=user).select_related(
        "document",
        "question_set",
    )

    nlp_attempts = all_attempts.filter(question_set__generation_mode="nlp")
    ai_attempts = all_attempts.filter(question_set__generation_mode="ai")

    ai_solver_attempts = AIQuizAttempt.objects.filter(quiz_attempt__user=user)
    ai_solver_nlp_attempts = ai_solver_attempts.filter(
        quiz_attempt__question_set__generation_mode="nlp"
    )
    ai_solver_ai_attempts = ai_solver_attempts.filter(
        quiz_attempt__question_set__generation_mode="ai"
    )

    recent_attempts = []

    for attempt in all_attempts.order_by("-completed_at")[:10]:
        recent_attempts.append({
            "id": attempt.id,
            "question_set_id": attempt.question_set_id,
            "generation_mode": attempt.question_set.generation_mode,
            "difficulty": attempt.question_set.difficulty,
            "user_attempt_number": get_user_attempt_number(user.id, attempt.id),
            "user_document_number": get_user_document_number(user.id, attempt.document_id),
            "score": attempt.score,
            "total_questions": attempt.total_questions,
            "completed_at": attempt.completed_at,
        })

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "date_joined": user.date_joined,
        },
        "documents_count": Document.objects.filter(user=user).count(),
        "question_sets_count": QuestionSet.objects.filter(document__user=user).count(),
        "definitions_count": ExtractedDefinition.objects.filter(document__user=user).count(),
        "questions_count": GeneratedQuestion.objects.filter(document__user=user).count(),
        "overall": build_attempt_stats(all_attempts),
        "nlp": build_attempt_stats(nlp_attempts),
        "ai": build_attempt_stats(ai_attempts),
        "ai_solver_overall": build_ai_attempt_stats(ai_solver_attempts),
        "ai_solver_nlp": build_ai_attempt_stats(ai_solver_nlp_attempts),
        "ai_solver_ai": build_ai_attempt_stats(ai_solver_ai_attempts),
        "user_vs_ai_overall": build_user_vs_ai_stats(all_attempts),
        "user_vs_ai_nlp": build_user_vs_ai_stats(nlp_attempts),
        "user_vs_ai_ai": build_user_vs_ai_stats(ai_attempts),
        "most_wrong_concepts": build_most_wrong_concepts_for_user(user, limit=10),
        "recent_attempts": recent_attempts,
    }


class AdminOverviewView(APIView):
    permission_classes = [IsAdminPanelUser]

    # intoarcem statisticile globale pentru dashboardul de admin
    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()

        total_documents = Document.objects.count()
        total_question_sets = QuestionSet.objects.count()
        total_definitions = ExtractedDefinition.objects.count()
        total_questions = GeneratedQuestion.objects.count()
        total_attempts = QuizAttempt.objects.count()

        total_answers = QuizAnswer.objects.count()
        correct_answers = QuizAnswer.objects.filter(is_correct=True).count()
        wrong_answers = QuizAnswer.objects.filter(is_correct=False).count()

        average_score = QuizAttempt.objects.aggregate(avg=Avg("score"))["avg"] or 0

        nlp_attempts = QuizAttempt.objects.filter(question_set__generation_mode="nlp")
        ai_attempts = QuizAttempt.objects.filter(question_set__generation_mode="ai")

        nlp_average_score = nlp_attempts.aggregate(avg=Avg("score"))["avg"] or 0
        ai_average_score = ai_attempts.aggregate(avg=Avg("score"))["avg"] or 0

        data = {
            "total_users": total_users,
            "active_users": active_users,
            "staff_users": staff_users,
            "total_documents": total_documents,
            "total_question_sets": total_question_sets,
            "total_definitions": total_definitions,
            "total_questions": total_questions,
            "total_attempts": total_attempts,
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "average_score": round(average_score, 2),
            "nlp_attempts": nlp_attempts.count(),
            "ai_attempts": ai_attempts.count(),
            "nlp_average_score": round(nlp_average_score, 2) if nlp_average_score else 0,
            "ai_average_score": round(ai_average_score, 2) if ai_average_score else 0,
        }

        serializer = AdminOverviewSerializer(data)
        return Response(serializer.data)


class AdminAiOverviewView(APIView):
    permission_classes = [IsAdminPanelUser]

    # intoarcem statisticile globale pentru solverul AI
    def get(self, request):
        ai_attempts = AIQuizAttempt.objects.select_related("quiz_attempt", "quiz_attempt__question_set")

        overall = build_ai_attempt_stats(ai_attempts)
        nlp = build_ai_attempt_stats(
            ai_attempts.filter(quiz_attempt__question_set__generation_mode="nlp")
        )
        ai = build_ai_attempt_stats(
            ai_attempts.filter(quiz_attempt__question_set__generation_mode="ai")
        )

        data = {
            "overall": overall,
            "nlp": nlp,
            "ai": ai,
        }

        serializer = AdminAiOverviewSerializer(data)
        return Response(serializer.data)


class AdminUsersListView(APIView):
    permission_classes = [IsAdminPanelUser]

    # construim lista utilizatorilor pentru admin
    def get(self, request):
        users = User.objects.all().order_by("-date_joined")
        results = []

        for user in users:
            all_attempts = QuizAttempt.objects.filter(user=user)
            avg_score = all_attempts.aggregate(avg=Avg("score"))["avg"] or 0

            results.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
                "documents_count": Document.objects.filter(user=user).count(),
                "question_sets_count": QuestionSet.objects.filter(document__user=user).count(),
                "attempts_count": all_attempts.count(),
                "average_score": round(avg_score, 2) if avg_score else 0,
                "correct_answers": QuizAnswer.objects.filter(
                    attempt__user=user,
                    is_correct=True,
                ).count(),
                "wrong_answers": QuizAnswer.objects.filter(
                    attempt__user=user,
                    is_correct=False,
                ).count(),
            })

        serializer = AdminUserSerializer(results, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminPanelUser]

    # intoarcem dashboardul complet pentru un utilizator anume
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilizatorul nu a fost găsit."},
                status=404,
            )

        data = build_user_dashboard_data(user)
        serializer = AdminUserDetailSerializer(data)
        return Response(serializer.data)


class AdminDocumentsListView(APIView):
    permission_classes = [IsAdminPanelUser]

    # construim lista documentelor din platforma
    def get(self, request):
        documents = (
            Document.objects
            .select_related("user")
            .order_by("-uploaded_at")
        )

        results = []

        for document in documents:
            results.append({
                "id": document.id,
                "username": document.user.username,
                "full_name": f"{document.user.first_name} {document.user.last_name}".strip(),
                "email": document.user.email,
                "user_document_number": get_user_document_number(document.user_id, document.id),
                "file": document.file.url if document.file else "",
                "uploaded_at": document.uploaded_at,
                "definitions_count": ExtractedDefinition.objects.filter(document=document).count(),
                "nlp_definitions_count": ExtractedDefinition.objects.filter(
                    document=document,
                    generation_mode="nlp",
                ).count(),
                "ai_definitions_count": ExtractedDefinition.objects.filter(
                    document=document,
                    generation_mode="ai",
                ).count(),
                "questions_count": GeneratedQuestion.objects.filter(document=document).count(),
                "question_sets_count": QuestionSet.objects.filter(document=document).count(),
            })

        serializer = AdminDocumentSerializer(results, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class AdminQuestionSetsListView(APIView):
    permission_classes = [IsAdminPanelUser]

    # returnam toate seturile de quiz generate
    def get(self, request):
        question_sets = (
            QuestionSet.objects
            .select_related("document", "document__user")
            .order_by("-created_at")
        )

        results = []

        for question_set in question_sets:
            results.append({
                "id": question_set.id,
                "document_id": question_set.document_id,
                "username": question_set.document.user.username,
                "generation_mode": question_set.generation_mode,
                "difficulty": question_set.difficulty,
                "max_questions": question_set.max_questions,
                "questions_count": question_set.questions.count(),
                "created_at": question_set.created_at,
            })

        serializer = AdminQuestionSetSerializer(results, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class AdminAttemptsListView(APIView):
    permission_classes = [IsAdminPanelUser]

    # construim istoricul global al attempturilor utilizatorilor
    def get(self, request):
        attempts = (
            QuizAttempt.objects
            .select_related("user", "document", "question_set")
            .order_by("-completed_at")
        )

        results = []

        for attempt in attempts:
            ai_attempt = getattr(attempt, "ai_attempt", None)

            results.append({
                "id": attempt.id,
                "username": attempt.user.username,
                "full_name": f"{attempt.user.first_name} {attempt.user.last_name}".strip(),
                "email": attempt.user.email,
                "user_attempt_number": get_user_attempt_number(attempt.user_id, attempt.id),
                "user_document_number": get_user_document_number(attempt.user_id, attempt.document_id),
                "question_set_id": attempt.question_set_id,
                "generation_mode": attempt.question_set.generation_mode,
                "difficulty": attempt.question_set.difficulty,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "ai_score": ai_attempt.score if ai_attempt else None,
                "completed_at": attempt.completed_at,
                "time_spent_seconds": attempt.time_spent_seconds,
                "ai_time_spent_seconds": ai_attempt.time_spent_seconds if ai_attempt else 0,
            })

        serializer = AdminAttemptSerializer(results, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class AdminToggleUserActiveView(APIView):
    permission_classes = [IsAdminPanelUser]

    # schimbam starea activa sau inactiva a unui utilizator
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilizatorul nu a fost găsit."},
                status=404,
            )

        if user.id == request.user.id:
            return Response(
                {"error": "Nu îți poți dezactiva propriul cont din panoul de admin."},
                status=400,
            )

        serializer = ToggleUserActiveSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user.is_active = serializer.validated_data["is_active"]
        user.save()

        return Response({
            "message": "Starea utilizatorului a fost actualizată.",
            "is_active": user.is_active,
        })


class AdminDeleteDocumentView(APIView):
    permission_classes = [IsAdminPanelUser]

    # permitem stergerea unui document direct din panoul de admin
    def delete(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response(
                {"error": "Documentul nu a fost găsit."},
                status=404,
            )

        document.delete()

        return Response({
            "message": "Documentul a fost șters cu succes.",
        })