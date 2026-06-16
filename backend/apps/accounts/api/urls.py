from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ConsentListView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)

app_name = "accounts"

urlpatterns = [
    # Autenticação
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="refresh"),
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/password-reset", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "auth/password-reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    # Conta
    path("me", MeView.as_view(), name="me"),
    path("consents", ConsentListView.as_view(), name="consents"),
]
