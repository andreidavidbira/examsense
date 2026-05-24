from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from .throttles import (
    LoginRateThrottle,
    PasswordChangeRateThrottle,
    RegisterRateThrottle,
)


User = get_user_model()
password_reset_token_generator = PasswordResetTokenGenerator()


# setam cookie-urile de autentificare dupa login sau refresh
def set_auth_cookies(response, access_token=None, refresh_token=None):
    common_kwargs = {
        "httponly": True,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "path": settings.AUTH_COOKIE_PATH,
    }

    if access_token:
        response.set_cookie(
            key=settings.AUTH_COOKIE_ACCESS,
            value=access_token,
            max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
            **common_kwargs,
        )

    if refresh_token:
        response.set_cookie(
            key=settings.AUTH_COOKIE_REFRESH,
            value=refresh_token,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            **common_kwargs,
        )


# stergem cookie-urile de autentificare la logout sau dupa schimbarea parolei
def clear_auth_cookies(response):
    response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path=settings.AUTH_COOKIE_PATH)
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path=settings.AUTH_COOKIE_PATH)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieView(APIView):
    permission_classes = [AllowAny]

    # setam cookie-ul csrf pentru frontend
    def get(self, request):
        return Response({"message": "CSRF cookie set."}, status=200)


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    # cream un cont nou daca datele trimise sunt valide
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)

        return Response(serializer.errors, status=400)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    # autentificam utilizatorul si salvam tokenurile in cookie
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=400)

        user = authenticate(request, username=username, password=password)

        if not user:
            return Response({"error": "Invalid credentials."}, status=401)

        if not user.is_active:
            return Response({"error": "Account is inactive."}, status=403)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "message": "Login successful.",
            "user": UserSerializer(user).data,
        }, status=200)

        set_auth_cookies(
            response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return response


@method_decorator(csrf_protect, name="dispatch")
class RefreshCookieTokenView(APIView):
    permission_classes = [AllowAny]

    # generam un nou access token pe baza refresh tokenului din cookie
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if not refresh_token:
            return Response({"error": "Refresh token missing."}, status=401)

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        if not serializer.is_valid():
            return Response(serializer.errors, status=401)

        access_token = serializer.validated_data.get("access")
        new_refresh_token = serializer.validated_data.get("refresh")

        response = Response({"message": "Token refreshed."}, status=200)

        set_auth_cookies(
            response,
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    # facem logout si invalidam refresh tokenul curent daca exista
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass
            except Exception:
                pass

        response = Response({"message": "Logout successful."}, status=200)
        clear_auth_cookies(response)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    # returnam datele utilizatorului autentificat
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    # actualizam toate datele principale ale profilului
    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)

        return Response(serializer.errors, status=400)

    # permitem si actualizarea partiala a profilului
    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)

        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [PasswordChangeRateThrottle]

    # schimbam parola si fortam reautentificarea utilizatorului
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
                status=400,
            )

        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        user.set_password(new_password)
        user.save()

        response = Response({
            "message": "Parola a fost schimbata cu succes. Autentifica-te din nou.",
            "logout_required": True,
        }, status=200)

        clear_auth_cookies(response)
        return response


@method_decorator(csrf_protect, name="dispatch")
class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    # trimitem linkul de resetare daca exista un cont cu emailul respectiv
    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token_generator.make_token(user)
            reset_link = f"http://localhost:5173/reset-password?uid={uid}&token={token}"

            send_mail(
                subject="ExamSense+ - Resetare parolă",
                message=(
                    "Ai cerut resetarea parolei.\n\n"
                    f"Accesează linkul următor pentru a seta o parolă nouă:\n{reset_link}\n\n"
                    "Dacă nu ai cerut tu acest lucru, poți ignora acest email."
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@examsense.local"),
                recipient_list=[email],
                fail_silently=False,
            )

        return Response({
            "message": "Dacă există un cont cu acest email, a fost trimis un link de resetare.",
        }, status=200)


@method_decorator(csrf_protect, name="dispatch")
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    # resetam parola pe baza tokenului primit prin email
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response({"error": "Link invalid sau expirat."}, status=400)

        if not password_reset_token_generator.check_token(user, token):
            return Response({"error": "Link invalid sau expirat."}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Parola a fost resetată cu succes."}, status=200)