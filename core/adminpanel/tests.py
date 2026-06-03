"""
ExamSense+ - Admin Panel Tests
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- verifica securitatea si endpoint-urile principale din admin panel
- testeaza accesul permis pentru admin si blocat pentru user normal
- valideaza actiunile administrative de baza

Flow general:
- creeaza un utilizator admin si unul normal
- verifica accesul la endpoint-urile de administrare
- testeaza reguli importante precum blocarea dezactivarii propriului cont
- verifica stergerea documentelor din admin
"""

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document


User = get_user_model()


class AdminPanelApiTests(APITestCase):
    # pregatim un admin si un utilizator normal pentru testele de permisiuni
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="adminuser@example.com",
            password="ParolaTest123!",
            is_staff=True,
            is_superuser=True,
        )

        self.normal_user = User.objects.create_user(
            username="normaluser",
            email="normaluser@example.com",
            password="ParolaTest123!",
        )

    # verificam daca adminul poate accesa overview-ul global
    def test_admin_overview_is_accessible_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/adminpanel/overview/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_users", response.data)
        self.assertIn("total_documents", response.data)

    # verificam daca un user normal este blocat la accesarea admin panel-ului
    def test_admin_overview_is_forbidden_for_normal_user(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get("/api/adminpanel/overview/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # verificam regula care impiedica adminul sa isi dezactiveze propriul cont
    def test_admin_cannot_deactivate_own_account(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            f"/api/adminpanel/users/{self.admin_user.id}/toggle-active/",
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    # verificam daca adminul poate sterge un document existent
    def test_admin_can_delete_document(self):
        document = Document.objects.create(
            user=self.normal_user,
            file="documents/admin_delete.pdf",
            extracted_text="text",
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/api/adminpanel/documents/{document.id}/delete/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Document.objects.filter(id=document.id).exists())