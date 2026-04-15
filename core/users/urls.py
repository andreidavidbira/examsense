from django.urls import path
from .views import RegisterView
from .views import ProtectedView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('me/', ProtectedView.as_view()),
]