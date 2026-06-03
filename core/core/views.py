"""
ExamSense+ - Rate Limit Error Handler
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste raspunsul standard returnat atunci cand o cerere este blocata de rate limiting
- intoarce un mesaj JSON simplu si usor de procesat de frontend
- uniformizeaza tratarea erorilor de tip too many requests in proiect
"""

from django.http import JsonResponse


# intoarce raspunsul standard pentru cererile respinse din cauza limiterii de rata
def ratelimited_error(request, exception):
    return JsonResponse(
        {"error": "Too many requests. Please try again later."},
        status=429
    )