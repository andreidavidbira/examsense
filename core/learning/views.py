from django.db.models import Avg, Count, Max, Min

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import AIQuizAttempt, Document, GeneratedQuestion, QuizAnswer, QuizAttempt
from .serializers import (
    LearningDashboardSerializer,
    RecommendationSerializer,
    RetryQuizResponseSerializer,
    WeakConceptSerializer,
)


def get_user_document_number(user, document_id):
    try:
        document_obj = Document.objects.get(id=document_id, user=user)
    except Document.DoesNotExist:
        return None

    return (
        Document.objects
        .filter(user=user, id__lte=document_obj.id)
        .count()
    )


def get_user_attempt_number(user, attempt_id):
    return (
        QuizAttempt.objects
        .filter(user=user, id__lte=attempt_id)
        .count()
    )


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

    attempts_with_ai = attempts_queryset.select_related("ai_attempt")

    for attempt in attempts_with_ai:
        ai_attempt = getattr(attempt, "ai_attempt", None)

        if not ai_attempt:
            continue

        if attempt.score > ai_attempt.score:
            user_wins += 1
        elif attempt.score < ai_attempt.score:
            ai_wins += 1
        else:
            ties += 1

    return {
        "total_attempts": total_attempts,
        "average_score": round(average_score, 2) if average_score else 0,
        "best_score": best_score or 0,
        "worst_score": worst_score or 0,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "ai_average_score": round(ai_average_score, 2) if ai_average_score else 0,
        "ai_best_score": ai_best_score or 0,
        "ai_wins": ai_wins,
        "user_wins": user_wins,
        "ties": ties,
    }


def build_weak_concepts(user, limit=10):
    wrong_answers = (
        QuizAnswer.objects
        .filter(attempt__user=user, is_correct=False)
        .select_related("question__document", "question__source_definition")
        .values(
            "question__source_definition__concept",
            "question__source_definition__definition",
            "question__document__id",
            "question__document__file",
        )
        .annotate(wrong_count=Count("id"))
        .order_by("-wrong_count")
    )

    results = []

    for item in wrong_answers:
        concept = item["question__source_definition__concept"]

        if not concept:
            continue

        document_id = item["question__document__id"]
        document_file = item["question__document__file"]

        user_document_number = None
        if document_id:
            user_document_number = get_user_document_number(user, document_id)

        results.append({
            "concept": concept,
            "definition": item.get("question__source_definition__definition") or "",
            "wrong_count": item["wrong_count"],
            "document_id": document_id,
            "document_file": f"/media/{document_file}" if document_file else None,
            "user_document_number": user_document_number,
        })

        if len(results) >= limit:
            break

    return results


class LearningDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempts = (
            QuizAttempt.objects
            .filter(user=request.user)
            .select_related("document", "question_set", "ai_attempt")
            .order_by("-completed_at")
        )
        nlp_attempts = attempts.filter(question_set__generation_mode="nlp")
        ai_attempts = attempts.filter(question_set__generation_mode="ai")

        weak_concepts = build_weak_concepts(request.user, limit=5)

        recent_attempts = []

        for attempt in attempts[:5]:
            user_document_number = get_user_document_number(request.user, attempt.document.id)
            user_attempt_number = get_user_attempt_number(request.user, attempt.id)

            current_ai_score = 0
            ai_attempt = getattr(attempt, "ai_attempt", None)
            if ai_attempt:
                current_ai_score = ai_attempt.score

            recent_attempts.append({
                "attempt_id": attempt.id,
                "question_set_id": attempt.question_set.id,
                "generation_mode": attempt.question_set.generation_mode,
                "user_attempt_number": user_attempt_number,
                "document_id": attempt.document.id,
                "user_document_number": user_document_number,
                "document_file": attempt.document.file.url if attempt.document.file else None,
                "score": attempt.score,
                "ai_score": current_ai_score,
                "total_questions": attempt.total_questions,
                "completed_at": attempt.completed_at,
            })

        response_data = {
            "overall": build_mode_stats(attempts),
            "nlp": build_mode_stats(nlp_attempts),
            "ai": build_mode_stats(ai_attempts),
            "weak_concepts": weak_concepts,
            "recent_attempts": recent_attempts,
        }

        serializer = LearningDashboardSerializer(response_data)
        return Response(serializer.data)


class WeakConceptsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        weak_concepts = build_weak_concepts(request.user, limit=20)
        serializer = WeakConceptSerializer(weak_concepts, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class RecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        weak_concepts = build_weak_concepts(request.user, limit=10)

        recommendations = []

        for item in weak_concepts:
            wrong_count = item["wrong_count"]

            if wrong_count >= 5:
                recommendation_text = (
                    "Concept prioritar pentru recapitulare imediata. Revino asupra definitiei, "
                    "refa quiz-uri pe acest subiect si incearca sa il explici in cuvintele tale."
                )
            elif wrong_count >= 3:
                recommendation_text = (
                    "Concept recomandat pentru exersare suplimentara. Reciteste definitia si "
                    "rezolva inca un set de intrebari pentru consolidare."
                )
            else:
                recommendation_text = (
                    "Concept util pentru consolidare. O scurta recapitulare este suficienta "
                    "pentru a-l fixa mai bine."
                )

            recommendations.append({
                "concept": item["concept"],
                "definition": item.get("definition", ""),
                "wrong_count": wrong_count,
                "recommendation": recommendation_text,
                "document_id": item.get("document_id"),
                "document_file": item.get("document_file"),
                "user_document_number": item.get("user_document_number"),
            })

        serializer = RecommendationSerializer(recommendations, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class RetryQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        weak_concepts = build_weak_concepts(request.user, limit=10)
        concept_names = [item["concept"] for item in weak_concepts]

        if not concept_names:
            return Response({
                "count": 0,
                "questions": [],
                "message": "Nu exista suficiente concepte gresite pentru un quiz de recapitulare.",
            })

        questions = (
            GeneratedQuestion.objects
            .filter(
                document__user=request.user,
                source_definition__concept__in=concept_names,
            )
            .select_related("source_definition", "question_set")
            .order_by("?")
            .distinct()
        )

        question_list = []

        for question in questions[:10]:
            question_list.append({
                "id": question.id,
                "question_set_id": question.question_set.id,
                "generation_mode": question.generation_mode,
                "question_type": question.question_type,
                "language": question.language,
                "question_text": question.question_text,
                "options": question.options,
                "correct_answer": question.correct_answer,
            })

        response_data = {
            "count": len(question_list),
            "questions": question_list,
        }

        serializer = RetryQuizResponseSerializer(response_data)
        return Response(serializer.data)