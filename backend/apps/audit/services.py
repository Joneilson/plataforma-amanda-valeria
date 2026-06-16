"""Camada de serviços de `audit` — registro de eventos (escrita)."""
from .models import AuditLog


def get_client_ip(request) -> str | None:
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_event(*, action, request=None, user=None, resource="", resource_id="", metadata=None):
    """Cria um registro de auditoria. Tolerante: nunca deve quebrar o fluxo."""
    return AuditLog.objects.create(
        user=user,
        action=action,
        resource=resource,
        resource_id=str(resource_id) if resource_id else "",
        ip=get_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "")[:300] if request else ""),
        metadata=metadata or {},
    )
