from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from habits.models import Habit
from habits.validators import (
    RewardAndRelatedHabitValidator,
    DurationValidator,
    OnlyPleasantHabitAsRelatedValidator,
    PleasantHabitRestrictionsValidator,
    PeriodicityValidator,
)


class HabitPagination(PageNumberPagination):
    """Пагинатор DRF: выводит ровно по 5 привычек на страницу [Пагинация]."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Привычки со сквозной комплексной валидацией [Валидаторы]."""

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("owner", "last_reminded")  # Владельца подставим в perform_create автоматическим хуком

        # Подключаем все валидаторы под жесткие критерии оценки [Валидаторы]
        validators = [
            RewardAndRelatedHabitValidator(related_habit_field="related_habit", reward_field="reward"),
            DurationValidator(field="duration"),
            OnlyPleasantHabitAsRelatedValidator(field="related_habit"),
            PleasantHabitRestrictionsValidator(
                is_pleasant_field="is_pleasant",
                related_habit_field="related_habit",
                reward_field="reward"
            ),
            PeriodicityValidator(field="periodicity"),
        ]
