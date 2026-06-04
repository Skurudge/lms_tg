from django.urls import path
from rest_framework.routers import DefaultRouter

from habits.apps import HabitsConfig
from habits.views import HabitViewSet, PublicHabitListAPIView

app_name = HabitsConfig.name

router = DefaultRouter()
router.register(r"my-habits", HabitViewSet, basename="my_habits")

urlpatterns = [
    # Список публичных привычек платформы [Эндпоинты]
    path("public/", PublicHabitListAPIView.as_view(), name="public_habits"),
] + router.urls
