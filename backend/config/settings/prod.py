"""Configurações de produção — endurecimento de segurança."""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False

# Fail-hard: subir em produção sem chaves fortes cifraria o prontuário com uma
# chave derivada do default inseguro — melhor recusar o boot.
if SECRET_KEY == "insecure-dev-key-change-me":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY é obrigatória em produção.")
if not FIELD_ENCRYPTION_KEY:  # noqa: F405
    raise ImproperlyConfigured(
        "FIELD_ENCRYPTION_KEY é obrigatória em produção (dados clínicos cifrados). "
        "Gere com: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    )

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])  # noqa: F405
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=CORS_ALLOWED_ORIGINS)  # noqa: F405

# HTTPS / cookies seguros
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
