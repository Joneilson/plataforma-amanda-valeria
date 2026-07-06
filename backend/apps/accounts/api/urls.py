from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ConsentListView,
    ConsentPendingView,
    DataExportView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)

app_name = "accounts"

urlpatterns = [
    # Autenticação (login por username — contas criadas pela psicóloga)
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/password-reset", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "auth/password-reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    # Conta
    path("me", MeView.as_view(), name="me"),
    path("me/export", DataExportView.as_view(), name="data-export"),
    path("consents", ConsentListView.as_view(), name="consents"),
    path("consents/pending", ConsentPendingView.as_view(), name="consents-pending"),
]
