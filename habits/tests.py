from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from habits.models import Habit


class HabitTestCase(APITestCase):
    """Комплексный класс тестирования CRUD, ролей доступов и бизнес-валидаторов (Критерий оценки)."""

    def setUp(self):
        """Заполнение тестовой базы данных перед каждым запуском тестов."""
        # Создаем пользователей
        self.user_owner = User.objects.create_user(email="owner@test.com", password="password123")
        self.user_other = User.objects.create_user(email="other@test.com", password="password123")

        # Создаем базовую полезную привычку для владельца
        self.habit = Habit.objects.create(
            owner=self.user_owner,
            place="Дом",
            time="08:00:00",
            action="Сделать зарядку",
            duration=60,
            periodicity=1,
            is_public=False
        )

        # Создаем приятную привычку для тестов связывания
        self.pleasant_habit = Habit.objects.create(
            owner=self.user_owner,
            place="Ванная",
            time="08:15:00",
            action="Принять контрастный душ",
            is_pleasant=True,
            duration=90,
            periodicity=1
        )

    # ==================== ТЕСТИРОВАНИЕ CRUD И ДОСТУПОВ ====================

    def test_create_habit_success(self):
        """Успешное создание личной полезной привычки авторизованным владельцем."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        data = {
            "place": "Офис",
            "time": "12:00:00",
            "action": "Выпить стакан воды",
            "duration": 30,
            "periodicity=1": 1
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(action="Выпить стакан воды").count(), 1)
        self.assertEqual(Habit.objects.get(action="Выпить стакан воды").owner, self.user_owner)

    def test_get_my_habits_list(self):
        """Получение списка личных привычек с проверкой пагинации (вывод по 5 элементов)."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # Проверка структуры пагинации DRF

    def test_get_habit_by_other_user_denied(self):
        """Запрет просмотра чужой приватной привычки посторонним пользователем."""
        self.client.force_authenticate(user=self.user_other)
        url = reverse("habits:my_habits-detail", kwargs={"pk": self.habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Скрывается через get_queryset

    def test_delete_habit_by_owner(self):
        """Владелец может беспрепятственно удалить свою личную привычку."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-detail", kwargs={"pk": self.habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(pk=self.habit.pk).count(), 0)

    def test_get_public_habits_list(self):
        """Доступность публичного эндпоинта для всех авторизованных пользователей."""
        # Делаем привычку публичной
        self.habit.is_public = True
        self.habit.save()

        self.client.force_authenticate(user=self.user_other)
        url = reverse("habits:public_habits")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    # ==================== ТЕСТИРОВАНИЕ ВАЛИДАТОРОВ БИЗНЕС-ЛОГИКИ ====================

    def test_validator_simultaneous_reward_and_related_habit(self):
        """Ошибка: Нельзя одновременно указывать текстовое вознаграждение и связанную привычку."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        data = {
            "place": "Парк",
            "time": "18:00:00",
            "action": "Пробежка",
            "reward": "Съесть пирожное",
            "related_habit": self.pleasant_habit.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_validator_duration_limit(self):
        """Ошибка: Время выполнения атомной привычки не должно превышать 120 секунд."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        data = {
            "place": "Дом",
            "time": "07:00:00",
            "action": "Чтение книги",
            "duration": 150  # Больше 120 секунд по ТЗ
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_only_pleasant_habit_as_related(self):
        """Ошибка: В качестве связанной привычки можно выбрать только приятную привычку."""
        # Создаем вторую ПОЛЕЗНУЮ привычку (is_pleasant=False)
        useful_habit_2 = Habit.objects.create(
            owner=self.user_owner, place="Зал", time="19:00:00", action="Тяга штанги", duration=60
        )

        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        data = {
            "place": "Дом",
            "time": "20:00:00",
            "action": "Ужин",
            "related_habit": useful_habit_2.id  # Ошибка: привязываем полезную вместо приятной
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_pleasant_habit_restrictions(self):
        """Ошибка: У приятной привычки не может быть своего вознаграждения или связанной привычки."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        data = {
            "place": "Ванная",
            "time": "22:00:00",
            "action": "Принять пенную ванну",
            "is_pleasant": True,
            "reward": "Включить музыку"  # Ошибка: награда для награды
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_periodicity_limit(self):
        """Ошибка: Периодичность выполнения привычки не должна быть реже, чем 1 раз в 7 дней."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("habits:my_habits-list")
        data = {
            "place": "Спортзал",
            "time": "10:00:00",
            "action": "Тяжелая тренировка",
            "periodicity": 10  # Ошибка: раз в 10 дней (ТЗ требует не реже 1 раза в 7 дней)
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
