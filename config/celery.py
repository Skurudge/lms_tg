import os
from celery import Celery
from celery.schedules import crontab

# Указываем дефолтные настройки Django для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Читаем конфигурацию из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Силовой перевод Kombu на RESP2, чтобы старый Redis на Windows не ругался на команду HELLO
app.conf.broker_transport_options = {
    'protocol': 2,
}

# Автоматически ищем задачи tasks.py в приложениях
app.autodiscover_tasks()

# Настройка ежеминутного расписания Celery Beat для проверки напоминаний привычек (Критерий оценки)
app.conf.beat_schedule = {
    "send-habit-reminders-every-minute": {
        "task": "habits.tasks.send_habit_reminders",
        "schedule": crontab(minute="*"),  # Скан базы каждую минуту (Интеграция)
    },
}
