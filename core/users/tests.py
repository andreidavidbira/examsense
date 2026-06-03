"""
ExamSense+ - Users Tests
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- verifica flow-urile principale din modulul users
- testeaza register, login si accesul la endpoint-ul me
- valideaza comportamentul de baza al autentificarii

Flow general:
- trimite request-uri catre endpoint-urile de autentificare
- verifica status code-urile si structura raspunsurilor
- confirma ca utilizatorii sunt creati si autentificati corect
"""

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UsersApiTests(APITestCase):
    # verificam daca un utilizator nou se poate inregistra cu date valide
    def test_register_success(self):
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "ParolaTest123!",
            "password_confirm": "ParolaTest123!",
        }

        response = self.client.post("/api/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "testuser")
        self.assertTrue(User.objects.filter(username="testuser").exists())

    # verificam daca inregistrarea este blocata cand parolele nu coincid
    def test_register_fails_when_passwords_do_not_match(self):
        payload = {
            "username": "user2",
            "email": "user2@example.com",
            "first_name": "User",
            "last_name": "Two",
            "password": "ParolaTest123!",
            "password_confirm": "AltaParola123!",
        }

        response = self.client.post("/api/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    # verificam daca login-ul reusit intoarce datele userului si seteaza cookie-urile
    def test_login_success_sets_auth_cookies(self):
        User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="ParolaTest123!",
            first_name="Login",
            last_name="User",
        )

        payload = {
            "username": "loginuser",
            "password": "ParolaTest123!",
        }

        response = self.client.post("/api/auth/login/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    # verificam daca login-ul esueaza atunci cand credentialele sunt gresite
    def test_login_fails_with_invalid_credentials(self):
        User.objects.create_user(
            username="badlogin",
            email="badlogin@example.com",
            password="ParolaTest123!",
        )

        payload = {
            "username": "badlogin",
            "password": "gresita123",
        }

        response = self.client.post("/api/auth/login/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    # verificam daca endpoint-ul me returneaza corect datele utilizatorului autentificat
    def test_me_returns_authenticated_user_data(self):
        user = User.objects.create_user(
            username="meuser",
            email="meuser@example.com",
            password="ParolaTest123!",
            first_name="Me",
            last_name="User",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "meuser")
        self.assertEqual(response.data["email"], "meuser@example.com")