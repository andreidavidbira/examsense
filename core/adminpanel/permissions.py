"""
ExamSense+ - Admin Panel Permissions
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste permisiuni custom pentru zona de administrare
- limiteaza accesul la endpoint-urile din admin panel
- permite doar utilizatorilor autentificati cu drepturi de admin
"""

from rest_framework.permissions import BasePermission


class IsAdminPanelUser(BasePermission):
    # verifica daca utilizatorul curent este autentificat si are rol de admin
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )