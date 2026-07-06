"""Testes de autenticação — login, throttling, reset de senha e WebSocket JWT."""
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.messaging.middleware import _get_user

User = get_user_model()


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ana.silva", password="senha-forte-123", nome="Ana Silva"
        )

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_login_ok_retorna_tokens(self):
        resp = self.client.post(
            "/api/auth/login",
            {"username": "ana.silva", "password": "senha-forte-123"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_errado_retorna_401(self):
        resp = self.client.post(
            "/api/auth/login",
            {"username": "ana.silva", "password": "errada"},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_forca_bruta_bloqueada_pelo_throttle(self):
        # Escopo "login": 10/min. A 11ª tentativa deve ser bloqueada com 429.
        for _ in range(10):
            self.client.post(
                "/api/auth/login",
                {"username": "ana.silva", "password": "errada"},
                format="json",
            )
        resp = self.client.post(
            "/api/auth/login",
            {"username": "ana.silva", "password": "errada"},
            format="json",
        )
        self.assertEqual(resp.status_code, 429)


class PasswordResetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ana.silva",
            password="x",
            nome="Ana Silva",
            email="ana@exemplo.com",
        )

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_resposta_uniforme_nao_revela_se_email_existe(self):
        r1 = self.client.post(
            "/api/auth/password-reset", {"email": "ana@exemplo.com"}, format="json"
        )
        r2 = self.client.post(
            "/api/auth/password-reset", {"email": "nao-existe@exemplo.com"}, format="json"
        )
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r1.data, r2.data)
        # E-mail só é enviado para conta existente.
        self.assertEqual(len(mail.outbox), 1)


class WebSocketJWTMiddlewareTests(TestCase):
    """O WebSocket só pode aceitar ACCESS token de usuário ativo."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="ana.silva", password="x", nome="Ana Silva")

    def test_access_token_autentica(self):
        access = str(RefreshToken.for_user(self.user).access_token)
        result = async_to_sync(_get_user)(access)
        self.assertEqual(result, self.user)

    def test_refresh_token_e_rejeitado(self):
        refresh = str(RefreshToken.for_user(self.user))
        result = async_to_sync(_get_user)(refresh)
        self.assertIsInstance(result, AnonymousUser)

    def test_token_invalido_e_rejeitado(self):
        result = async_to_sync(_get_user)("token-adulterado")
        self.assertIsInstance(result, AnonymousUser)

    def test_usuario_desativado_e_rejeitado(self):
        access = str(RefreshToken.for_user(self.user).access_token)
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        result = async_to_sync(_get_user)(access)
        self.assertIsInstance(result, AnonymousUser)
