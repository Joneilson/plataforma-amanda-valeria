"""Configurações de desenvolvimento."""
from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Frontend Next.js em dev
CORS_ALLOWED_ORIGINS = [env("FRONTEND_URL", default="http://localhost:3000")]  # noqa: F405
CORS_ALLOW_CREDENTIALS = True
