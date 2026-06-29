"""Middleware JWT para Django Channels.

Lê o access token do query-string (?token=<access>) e injeta o
usuário autenticado no scope do WebSocket.
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()


@database_sync_to_async
def _get_user(token_key: str):
    try:
        UntypedToken(token_key)
    except (InvalidToken, TokenError):
        return AnonymousUser()
    from rest_framework_simplejwt.backends import TokenBackend
    from django.conf import settings

    data = TokenBackend(
        algorithm=settings.SIMPLE_JWT.get("ALGORITHM", "HS256"),
        signing_key=settings.SECRET_KEY,
    ).decode(token_key, verify=True)
    user_id = data.get("user_id")
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    """Autentica conexões WebSocket via query-string ?token=<access>."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        scope["user"] = await _get_user(token) if token else AnonymousUser()
        return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
