from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """Manager do usuário. Garante que superusuários tenham o papel de psicóloga."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "PSICOLOGA")
        return super().create_superuser(username, email, password, **extra_fields)
