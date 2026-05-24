from django.http import JsonResponse


def ratelimited_error(request, exception):
    return JsonResponse(
        {"error": "Too many requests. Please try again later."},
        status=429
    )