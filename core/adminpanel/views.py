from django.contrib.auth import get_user_model
from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.response import Response

from documents.models import Document, ExtractedDefinition, GeneratedQuestion, QuizAttempt
from .permissions import IsAdminPanelUser
from .serializers import (
    AdminOverviewSerializer,
    AdminUserSerializer,
    AdminDocumentSerializer,
    AdminAttemptSerializer,
    ToggleUserActiveSerializer,
)


User = get_user_model()


def get_user_document_number(user_id, document_id):
    return (
        Document.objects
        .filter(user_id=user_id, id__lte=document_id)
        .count()
    )


def get_user_attempt_number(user_id, attempt_id):
    return (
        QuizAttempt.objects
        .filter(user_id=user_id, id__lte=attempt_id)
        .count()
    )


class AdminOverviewView(APIView):
    permission_classes = [IsAdminPanelUser]

    def get(self, request):
        avg_score = QuizAttempt.objects.aggregate(avg=Avg("score"))["avg"] or 0

        data = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "staff_users": User.objects.filter(is_staff=True).count(),
            "total_documents": Document.objects.count(),
            "total_definitions": ExtractedDefinition.objects.count(),
            "total_questions": GeneratedQuestion.objects.count(),
            "total_attempts": QuizAttempt.objects.count(),
            "average_score": round(avg_score, 2),
        }

        serializer = AdminOverviewSerializer(data)
        return Response(serializer.data)


class AdminUsersListView(APIView):
    permission_classes = [IsAdminPanelUser]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")

        results = []
        for user in users:
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
                "attempts_count": QuizAttempt.objects.filter(user=user).count(),
            })

        serializer = AdminUserSerializer(results, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })


class AdminDocumentsListView(APIView):
    permission_classes = [IsAdminPanelUser]

    def get(self, request):
        documents = Document.objects.select_related("user").order_by("-uploaded_at")

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
                "questions_count": GeneratedQuestion.objects.filter(document=document).count(),
            })

        serializer = AdminDocumentSerializer(results, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })


class AdminAttemptsListView(APIView):
    permission_classes = [IsAdminPanelUser]

    def get(self, request):
        attempts = QuizAttempt.objects.select_related("user", "document").order_by("-completed_at")

        results = []
        for attempt in attempts:
            results.append({
                "id": attempt.id,
                "username": attempt.user.username,
                "full_name": f"{attempt.user.first_name} {attempt.user.last_name}".strip(),
                "email": attempt.user.email,
                "user_attempt_number": get_user_attempt_number(attempt.user_id, attempt.id),
                "user_document_number": get_user_document_number(attempt.user_id, attempt.document_id),
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "completed_at": attempt.completed_at,
            })

        serializer = AdminAttemptSerializer(results, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })


class AdminToggleUserActiveView(APIView):
    permission_classes = [IsAdminPanelUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Utilizatorul nu a fost găsit."}, status=404)

        if user.id == request.user.id:
            return Response({"error": "Nu îți poți dezactiva propriul cont din panoul de admin."}, status=400)

        serializer = ToggleUserActiveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user.is_active = serializer.validated_data["is_active"]
        user.save()

        return Response({
            "message": "Starea utilizatorului a fost actualizată.",
            "is_active": user.is_active
        })


class AdminDeleteDocumentView(APIView):
    permission_classes = [IsAdminPanelUser]

    def delete(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({"error": "Documentul nu a fost găsit."}, status=404)

        document.delete()
        return Response({"message": "Documentul a fost șters cu succes."})