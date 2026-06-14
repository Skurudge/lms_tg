from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Маршруты наших приложений
    path("api/users/", include("users.urls", namespace="users")),
    path("api/habits/", include("habits.urls", namespace="habits")),

    # Эндпоинты автогенерации интерактивной документации OpenAPI 3 (Критерий оценки)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
