from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Root URL → redirect to Django Swagger docs
    path(
        "",
        RedirectView.as_view(url="/api/docs/", permanent=False),
        name="root-redirect",
    ),
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/owners/", include("owners.urls")),
    path("api/stations/", include("stations.urls")),
    path("api/chargers/", include("chargers.urls")),
    path("api/slots/", include("slots.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/payments/", include("payments.urls")),
    # Django Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redirect /ai/ to FastAPI service
    path(
        "ai/",
        RedirectView.as_view(url="http://localhost:8001/", permanent=False),
        name="ai-redirect",
    ),
    path(
        "ai/docs/",
        RedirectView.as_view(url="http://localhost:8001/docs/", permanent=False),
        name="ai-docs-redirect",
    ),
    path(
        "ai/chat/",
        RedirectView.as_view(url="http://localhost:8001/chat/", permanent=False),
        name="ai-chat-redirect",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
