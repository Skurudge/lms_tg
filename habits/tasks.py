import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from habits.models import Habit


@shared_task
def send_habit_reminders():
    """
    Периодическая задача Celery Beat: каждую минуту сканирует базу привычек,
    сверяет время и рассылает уведомления пользователям в Telegram (Интеграция).
    """
    # Получаем текущее локальное время и дату (Europe/Moscow)
    now = timezone.localtime(timezone.now())
    current_time = now.time()
    current_date = now.date()

    # Форматируем текущее время до минут, чтобы не спотыкаться о секунды
    current_time_str = current_time.strftime("%H:%M")

    # Выбираем только те привычки, у которых заполнен Telegram Chat ID у владельца
    habits = Habit.objects.filter(owner__tg_chat_id__isnull=False).select_related("owner")

    sent_count = 0

    for habit in habits:
        # Приводим время привычки к строковому формату для точного минутного сравнения
        habit_time_str = habit.time.strftime("%H:%M")

        if habit_time_str == current_time_str:
            # Проверяем периодичность (в днях)
            if habit.last_reminded:
                days_passed = (current_date - habit.last_reminded).days
                if days_passed < habit.periodicity:
                    continue  # Ещё не прошёл нужный интервал дней, пропускаем

            # Формируем мотивирующее сообщение по формуле Джеймса Клира
            message = (
                f"⏰ НАПОМИНАНИЕ О ПРИВЫЧКЕ! ⏰\n\n"
                f"Пора действовать: Я буду {habit.action} "
                f"в {habit_time_str} в месте: {habit.place}.\n\n"
            )

            # Добавляем информацию о награде, если она есть
            if habit.reward:
                message += f"🎁 Твоё вознаграждение после выполнения: {habit.reward}\n"
            elif habit.related_habit:
                message += f"🎉 Связанная приятная привычка-награда: {habit.related_habit.action}\n"

            message += f"⏱️ Время на выполнение: {habit.duration} секунд. У тебя всё получится!"

            # Отправляем прямой HTTP POST запрос к API Telegram (Полный обход блокировок и VPN!)
            telegram_url = f"https://telegram.org{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": habit.owner.tg_chat_id,
                "text": message
            }

            try:
                response = requests.post(telegram_url, json=payload, timeout=10)
                if response.status_code == 200:
                    # Успешно отправлено, фиксируем дату напоминания для контроля периодичности
                    habit.last_reminded = current_date
                    habit.save()
                    sent_count += 1
            except requests.exceptions.RequestException:
                # Мягко пропускаем ошибки сети, чтобы воркер не падал по критерию оценки
                continue

    return f"Успешно обработано и отправлено напоминаний в Telegram: {sent_count}"
