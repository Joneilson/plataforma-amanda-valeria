from django.db import models


class TimeStampedModel(models.Model):
    """Base abstrata com timestamps de criação/atualização.

    Todas as entidades do domínio herdam desta classe para padronizar
    auditoria temporal básica.
    """

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)
