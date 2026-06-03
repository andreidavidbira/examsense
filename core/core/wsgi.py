"""
ExamSense+ - WSGI Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- initializeaza aplicatia Django in regim WSGI
- seteaza modulul principal de configurare al proiectului
- expune obiectul application folosit de server la rulare si deploy
"""

import os

from django.core.wsgi import get_wsgi_application


# setam fisierul principal de configurare pentru proiectul Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# expunem aplicatia WSGI folosita de server la rulare
application = get_wsgi_application()