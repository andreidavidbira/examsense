"""
ExamSense+ - Users Serializers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste serializer-ele pentru autentificare si gestionarea contului
- valideaza inregistrarea unui utilizator nou
- serializeaza datele utilizatorului pentru frontend
- valideaza actualizarea profilului, schimbarea parolei si resetarea parolei
- centralizeaza regulile de validare pentru datele introduse de utilizator
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


User = get_user_model()


# valideaza datele necesare pentru inregistrarea unui cont nou
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate_email(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Emailul este obligatoriu.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Exista deja un utilizator cu acest email.")

        return value.strip()

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Username-ul este obligatoriu.")

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Exista deja un utilizator cu acest username.")

        return value.strip()

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Prenumele este obligatoriu.")
        return value.strip()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Numele este obligatoriu.")
        return value.strip()

    # verifica daca parolele coincid si daca parola respecta regulile Django
    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Parolele nu coincid.",
            })

        validate_password(attrs["password"])
        return attrs

    # creeaza utilizatorul dupa ce toate datele au fost validate
    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        return user


# serializeaza datele utilizatorului pentru frontend
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "is_staff",
            "date_joined",
        ]


# valideaza modificarile aduse profilului utilizatorului
class UpdateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]

    def validate_email(self, value):
        user = self.instance

        if not value or not value.strip():
            raise serializers.ValidationError("Emailul este obligatoriu.")

        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Exista deja un utilizator cu acest email.")

        return value.strip()

    def validate_username(self, value):
        user = self.instance

        if not value or not value.strip():
            raise serializers.ValidationError("Username-ul este obligatoriu.")

        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Exista deja un utilizator cu acest username.")

        return value.strip()

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Prenumele este obligatoriu.")
        return value.strip()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Numele este obligatoriu.")
        return value.strip()


# valideaza schimbarea parolei pentru un utilizator autentificat
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({
                "new_password_confirm": "Parolele noi nu coincid.",
            })

        validate_password(attrs["new_password"])
        return attrs


# valideaza emailul folosit pentru cererea de resetare a parolei
class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Emailul este obligatoriu.")
        return value.strip()


# valideaza resetarea parolei pe baza uid-ului si tokenului primit
class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({
                "new_password_confirm": "Parolele nu coincid.",
            })

        validate_password(attrs["new_password"])
        return attrs