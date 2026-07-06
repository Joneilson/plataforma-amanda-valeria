"""Middleware JWT para Django Channels.

Lê o access token do query-string (?token=<access>) e injeta o
usuário autenticado no scope do WebSocket.
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def _get_user(token_key: str):
    # AccessToken valida assinatura, expiração E o tipo do token — um refresh
    # token (validade longa) não pode ser usado para abrir WebSocket.
    try:
        token = AccessToken(token_key)
    except (InvalidToken, TokenError):
        return AnonymousUser()
    try:
        return User.objects.get(pk=token.get("user_id"), is_active=True)
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
