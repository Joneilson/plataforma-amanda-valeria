"""Configurações base — comuns a todos os ambientes."""
from datetime import timedelta
from pathlib import Path

import environ

# backend/config/settings/base.py -> sobe 3 níveis até backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# .env fica na raiz do monorepo (um nível acima de backend/). Em Docker as
# variáveis vêm via env_file, então a ausência do arquivo é tolerada.
environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-me")
# Chave Fernet (base64 urlsafe, 32 bytes) para cifrar campos clínicos sensíveis.
# Sem valor, deriva-se da SECRET_KEY (apenas dev). Em produção, defina sempre.
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY", default="")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ---- Apps ----
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
]
LOCAL_APPS = [
    "apps.common",
    "apps.accounts",
    "apps.patients",
    "apps.scheduling",
    "apps.clinical",
    "apps.mood",
    "apps.homework",
    "apps.messaging",
    "apps.video",
    "apps.payments",
    "apps.resources",
    "apps.notifications",
    "apps.audit",
]
INSTALLED_APPS = ["daphne"] + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---- Banco de dados ----
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQL_DATABASE", default="amanda"),
        "USER": env("MYSQL_USER", default="amanda"),
        "PASSWORD": env("MYSQL_PASSWORD", default="amanda_pass"),
        "HOST": env("DB_HOST", default="db"),
        "PORT": env("DB_PORT", default="3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---- DRF + JWT ----
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("ACCESS_TOKEN_LIFETIME_MIN", default=30)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ---- E-mail / Frontend ----
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Amanda Valéria <nao-responder@amandavaleria.local>")

# ---- Redis / Channels / Celery ----
REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# ---- Integrações externas ----
DAILY_API_KEY = env("DAILY_API_KEY", default="")
BACKEND_URL = env("BACKEND_URL", default="http://localhost:8000")

# Dados PIX do recebedor (conta InfinityPay ou qualquer banco)
PIX_KEY = env("PIX_KEY", default="")        # chave PIX: email, CPF, telefone ou aleatória
PIX_TITULAR = env("PIX_TITULAR", default="Amanda Valeria")  # nome exibido no app do pagador
PIX_CIDADE = env("PIX_CIDADE", default="Recife")            # cidade do recebedor

# Link de pagamento por cartão (gerado no dashboard InfinityPay)
INFINITYPAY_LINK_CREDITO = env("INFINITYPAY_LINK_CREDITO", default="")

# ---- i18n / fuso ----
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True
CELERY_TIMEZONE = TIME_ZONE

# ---- Estáticos ----
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
