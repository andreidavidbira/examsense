"""
ExamSense+ - Custom API Throttles
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste throttle-uri custom pentru endpoint-urile sensibile ale aplicatiei
- permite aplicarea unor limite diferite pentru login, register, upload si submit quiz
- contribuie la securitatea backend-ului si la prevenirea abuzului asupra API-ului
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# limiteaza numarul de incercari de autentificare pentru utilizatorii anonimi
class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


# limiteaza numarul de inregistrari pentru utilizatorii anonimi
class RegisterRateThrottle(AnonRateThrottle):
    scope = "register"


# limiteaza numarul de upload-uri pentru utilizatorii autentificati
class UploadRateThrottle(UserRateThrottle):
    scope = "upload"


# limiteaza numarul de submit-uri de quiz pentru utilizatorii autentificati
class QuizSubmitRateThrottle(UserRateThrottle):
    scope = "quiz_submit"


# limiteaza numarul de schimbari de parola pentru utilizatorii autentificati
class PasswordChangeRateThrottle(UserRateThrottle):
    scope = "password_change"