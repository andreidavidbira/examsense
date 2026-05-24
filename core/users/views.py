from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer
)


User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)

        return Response(serializer.errors, status=400)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)

        return Response(serializer.errors, status=400)

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)

        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Parola veche este incorecta."]},
                status=400
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": "Parola a fost schimbata cu succes."})