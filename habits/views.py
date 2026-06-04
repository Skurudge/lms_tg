from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from habits.models import Habit
from habits.serializers import HabitSerializer, HabitPagination
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Кастомное разрешение: доступ разрешен только владельцу объекта [Права доступа]."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


@extend_schema_view(
    list=extend_schema(summary="Получить список личных привычек текущего пользователя с пагинацией"),
    create=extend_schema(summary="Создать новую привычку"),
    retrieve=extend_schema(summary="Просмотреть детали личной привычки"),
    update=extend_schema(summary="Полностью обновить личную привычку"),
    partial_update=extend_schema(summary="Частично обновить личную привычку"),
    destroy=extend_schema(summary="Удалить личную привычку"),
)
class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для реализации полного личного CRUD привычек пользователя [Эндпоинты, Права доступа].
    """
    serializer_class = HabitSerializer
    pagination_class = HabitPagination  # Пагинация по 5 элементов на страницу
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Возвращает привычки исключительно текущего авторизованного пользователя [Права доступа]."""
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Автоматическая привязка создаваемой привычки к текущему пользователю [Эндпоинты]."""
        serializer.save(owner=self.request.user)


@extend_schema(
    summary="Просмотр списка публичных привычек",
    description="Возвращает список всех привычек платформы, у которых признак публичности равен True [Эндпоинты]."
)
class PublicHabitListAPIView(generics.ListAPIView):
    """
    Эндпоинт для просмотра списка публичных привычек без возможности их изменения [Эндпоинты, Права доступа].
    """
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated]  # Доступно всем авторизованным пользователям
