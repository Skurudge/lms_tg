from django.conf import settings
from django.db import models


class Habit(models.Model):
    """
    Модель привычки согласно философии Джеймса Клира (Атомные привычки).
    Поддерживает полезные, приятные, связанные привычки и вознаграждения.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Владелец привычки",
    )
    place = models.CharField(max_length=255, verbose_name="Место выполнения")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.CharField(max_length=255, verbose_name="Действие")

    # Признак приятной привычки (используется как награда)
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")

    # Связанная привычка (указывается для полезных привычек, ведет на приятную)
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="useful_habits",
        verbose_name="Связанная приятная привычка",
    )

    # Периодичность выполнения в днях (по умолчанию ежедневная = 1)
    periodicity = models.PositiveIntegerField(default=1, verbose_name="Периодичность (в днях)")

    # Текстовое описание материального вознаграждения
    reward = models.CharField(max_length=255, blank=True, null=True, verbose_name="Вознаграждение")

    # Время на выполнение в секундах (по ТЗ атомная привычка должна быть не более 120 секунд)
    duration = models.PositiveIntegerField(default=60, verbose_name="Время на выполнение (в секундах)")

    # Признак общего публичного доступа
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")

    # Служебное поле для Celery-планировщика, чтобы не слать дубли напоминаний
    last_reminded = models.DateField(blank=True, null=True, verbose_name="Дата последнего напоминания")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["id"]

    def __str__(self):
        return f"{self.owner.email}: {self.action} в {self.time} ({self.place})"
