from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from users.models import User
from users.serializers import UserSerializer


@extend_schema(
    summary="Регистрация нового пользователя",
    description="Создает пользователя с уникальным email и хэширует пароль.",
    responses={201: UserSerializer}
)
class UserRegisterAPIView(generics.CreateAPIView):
    """Эндпоинт открытой регистрации пользователей (Критерий оценки)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
