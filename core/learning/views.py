from django.db.models import Avg, Count, Max, Min

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, GeneratedQuestion, QuizAnswer, QuizAttempt
from .serializers import (
    LearningDashboardSerializer,
    RecommendationSerializer,
    RetryQuizResponseSerializer,
    WeakConceptSerializer,
)


# calculam numarul documentului raportat doar la utilizatorul curent
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


# calculam numarul attemptului raportat doar la utilizatorul curent
def get_user_attempt_number(user, attempt_id):
    return (
        QuizAttempt.objects
        .filter(user=user, id__lte=attempt_id)
        .count()
    )


# construim lista conceptelor la care utilizatorul greseste cel mai des
def build_weak_concepts(user, limit=10):
    wrong_answers = (
        QuizAnswer.objects
        .filter(attempt__user=user, is_correct=False)
        .select_related("question__document", "question__source_definition")
        .values(
            "question__source_definition__concept",
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

    # returnam statisticile principale pentru dashboardul utilizatorului
    def get(self, request):
        attempts = QuizAttempt.objects.filter(user=request.user).order_by("-completed_at")
        answers = QuizAnswer.objects.filter(attempt__user=request.user)

        total_attempts = attempts.count()
        correct_answers = answers.filter(is_correct=True).count()
        wrong_answers = answers.filter(is_correct=False).count()

        average_score = attempts.aggregate(avg=Avg("score"))["avg"] or 0
        best_score = attempts.aggregate(best=Max("score"))["best"] or 0
        worst_score = attempts.aggregate(worst=Min("score"))["worst"] or 0

        weak_concepts = build_weak_concepts(request.user, limit=5)

        recent_attempts = []

        for attempt in attempts[:5]:
            user_document_number = get_user_document_number(request.user, attempt.document.id)
            user_attempt_number = get_user_attempt_number(request.user, attempt.id)

            recent_attempts.append({
                "attempt_id": attempt.id,
                "user_attempt_number": user_attempt_number,
                "document_id": attempt.document.id,
                "user_document_number": user_document_number,
                "document_file": attempt.document.file.url if attempt.document.file else None,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "completed_at": attempt.completed_at,
            })

        response_data = {
            "total_attempts": total_attempts,
            "average_score": round(average_score, 2) if average_score else 0,
            "best_score": best_score,
            "worst_score": worst_score,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "weak_concepts": weak_concepts,
            "recent_attempts": recent_attempts,
        }

        serializer = LearningDashboardSerializer(response_data)
        return Response(serializer.data)


class WeakConceptsView(APIView):
    permission_classes = [IsAuthenticated]

    # returnam lista extinsa cu conceptele slabe ale utilizatorului
    def get(self, request):
        weak_concepts = build_weak_concepts(request.user, limit=20)
        serializer = WeakConceptSerializer(weak_concepts, many=True)

        return Response({
            "count": len(serializer.data),
            "results": serializer.data,
        })


class RecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    # construim recomandari simple pe baza numarului de greseli
    def get(self, request):
        weak_concepts = build_weak_concepts(request.user, limit=10)

        recommendations = []

        for item in weak_concepts:
            wrong_count = item["wrong_count"]

            if wrong_count >= 5:
                recommendation_text = "Concept prioritar pentru recapitulare imediata."
            elif wrong_count >= 3:
                recommendation_text = "Concept recomandat pentru exersare suplimentara."
            else:
                recommendation_text = "Concept util pentru consolidare."

            recommendations.append({
                "concept": item["concept"],
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

    # generam un quiz de recapitulare pe baza conceptelor la care utilizatorul greseste
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
            .select_related("source_definition")
            .order_by("id")
            .distinct()
        )

        question_list = []
        seen_ids = set()

        for question in questions:
            if question.id in seen_ids:
                continue

            seen_ids.add(question.id)

            question_list.append({
                "id": question.id,
                "question_type": question.question_type,
                "language": question.language,
                "question_text": question.question_text,
                "options": question.options,
                "correct_answer": question.correct_answer,
            })

            if len(question_list) >= 10:
                break

        response_data = {
            "count": len(question_list),
            "questions": question_list,
        }

        serializer = RetryQuizResponseSerializer(response_data)
        return Response(serializer.data)