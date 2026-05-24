from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class RegisterRateThrottle(AnonRateThrottle):
    scope = "register"


class UploadRateThrottle(UserRateThrottle):
    scope = "upload"


class QuizSubmitRateThrottle(UserRateThrottle):
    scope = "quiz_submit"


class PasswordChangeRateThrottle(UserRateThrottle):
    scope = "password_change"