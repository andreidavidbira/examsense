"""
ExamSense+ - Project URL Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste rutele principale ale proiectului Django
- conecteaza modulele auth, documents, learning si adminpanel
- expune interfata Django Admin
- permite servirea fisierelor media in modul de dezvoltare
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# aici legam toate rutele principale ale proiectului
urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("users.urls")),
    path("api/documents/", include("documents.urls")),
    path("api/learning/", include("learning.urls")),
    path("api/adminpanel/", include("adminpanel.urls")),
]


# in modul de dezvoltare permitem accesul direct la fisierele media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)