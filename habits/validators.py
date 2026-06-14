from rest_framework.exceptions import ValidationError


class RewardAndRelatedHabitValidator:
    """Проверяет, что не указаны одновременно связанная привычка и вознаграждение [Валидаторы]."""
    def __init__(self, related_habit_field, reward_field):
        self.related_habit_field = related_habit_field
        self.reward_field = reward_field

    def __call__(self, attrs):
        related_habit = attrs.get(self.related_habit_field)
        reward = attrs.get(self.reward_field)

        if related_habit and reward:
            raise ValidationError(
                "Нельзя одновременно выбирать связанную привычку и указывать вознаграждение. Выберите что-то одно [Валидаторы]."
            )


class DurationValidator:
    """Проверяет, что время выполнения атомной привычки не превышает 120 секунд [Валидаторы]."""
    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        duration = attrs.get(self.field)
        if duration and duration > 120:
            raise ValidationError(
                f"Время выполнения привычки не должно превышать 120 секунд (2 минуты). Вы указали: {duration} [Валидаторы]."
            )


class OnlyPleasantHabitAsRelatedValidator:
    """Гарантирует, что в связанные привычки могут попадать только приятные привычки [Валидаторы]."""
    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        related_habit = attrs.get(self.field)
        if related_habit and not related_habit.is_pleasant:
            raise ValidationError(
                "В качестве связанной привычки может быть выбрана только привычка с признаком приятной [Валидаторы]."
            )


class PleasantHabitRestrictionsValidator:
    """Проверяет, что у приятной привычки нет вознаграждения или связанной привычки [Валидаторы]."""
    def __init__(self, is_pleasant_field, related_habit_field, reward_field):
        self.is_pleasant_field = is_pleasant_field
        self.related_habit_field = related_habit_field
        self.reward_field = reward_field

    def __call__(self, attrs):
        is_pleasant = attrs.get(self.is_pleasant_field, False)
        related_habit = attrs.get(self.related_habit_field)
        reward = attrs.get(self.reward_field)

        if is_pleasant:
            if related_habit or reward:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки [Валидаторы]."
                )


class PeriodicityValidator:
    """Запрещает выполнять привычку реже, чем 1 раз в 7 дней (интервал не более 7 дней) [Валидаторы]."""
    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        periodicity = attrs.get(self.field)
        if periodicity and periodicity > 7:
            raise ValidationError(
                f"Нельзя выполнять привычку реже, чем 1 раз в 7 дней. Максимальный интервал — 7. Вы указали: {periodicity} [Валидаторы]."
            )
