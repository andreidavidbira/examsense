"""
ExamSense+ - ASGI Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- initializeaza aplicatia Django in regim ASGI
- seteaza modulul principal de configurare al proiectului
- expune obiectul application folosit la rulare si deploy
"""

import os

from django.core.asgi import get_asgi_application


# setam fisierul principal de configurare pentru proiectul Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# expunem aplicatia ASGI folosita de server la rulare
application = get_asgi_application()