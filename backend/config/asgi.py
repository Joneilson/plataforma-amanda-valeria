import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

# Inicializa o Django antes de importar consumers/rotas que tocam models.
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # "websocket": ...  # adicionado na Fase 5 (chat) via apps.messaging.routing
    }
)
