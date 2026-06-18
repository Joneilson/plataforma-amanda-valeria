"""Campos de modelo compartilhados.

`EncryptedTextField` cifra conteúdo clínico sensível (🔒) em repouso, em nível
de aplicação — usado por humor, anotações, prontuário e mensagens.
"""
import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    """Instância Fernet a partir de FIELD_ENCRYPTION_KEY.

    Em produção, defina `FIELD_ENCRYPTION_KEY` (chave Fernet de 32 bytes em
    base64 urlsafe). Sem ela, deriva uma chave estável da SECRET_KEY — aceitável
    apenas em desenvolvimento.
    """
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", "") or ""
    if key:
        key_bytes = key.encode() if isinstance(key, str) else key
    else:
        digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        key_bytes = base64.urlsafe_b64encode(digest)
    return Fernet(key_bytes)


class EncryptedTextField(models.TextField):
    """TextField cifrado em repouso (Fernet). Transparente para a aplicação.

    O valor é cifrado ao gravar e decifrado ao ler. Tolerante a dados legados
    sem cifra (retornados como estão), o que permite adoção incremental.
    """

    _PREFIX = "enc:"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        token = _fernet().encrypt(value.encode()).decode()
        return f"{self._PREFIX}{token}"

    def from_db_value(self, value, expression, connection):
        if not value or not value.startswith(self._PREFIX):
            return value
        try:
            return _fernet().decrypt(value[len(self._PREFIX) :].encode()).decode()
        except InvalidToken:
            return value
