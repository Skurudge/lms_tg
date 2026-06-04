from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации и отображения профиля пользователя."""

    class Meta:
        model = User
        fields = ("id", "email", "password", "phone", "city", "tg_chat_id")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Хэшируем пароль при регистрации через менеджер (Критерий оценки)
        return User.objects.create_user(**validated_data)
