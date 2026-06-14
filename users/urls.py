from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import UserRegisterAPIView

app_name = UsersConfig.name

urlpatterns = [
    # Открытая регистрация (Критерий оценки)
    path("register/", UserRegisterAPIView.as_view(), name="register"),

    # Получение и обновление JWT-токенов (Критерий оценки)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
