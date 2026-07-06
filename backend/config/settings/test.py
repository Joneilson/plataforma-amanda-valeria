"""Configurações de teste — banco SQLite em memória, sem serviços externos.

Uso: python manage.py test --settings=config.settings.test
"""
from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-secret-key-nao-usar-em-producao"

# Banco em memória: testes não dependem do MySQL do Docker.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Sem Redis nos testes.
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}
CELERY_TASK_ALWAYS_EAGER = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Hasher rápido — acelera criação de usuários nos testes.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
