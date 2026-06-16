from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Consent, User


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "tipo", "versao", "created_at", "ip")
    list_filter = ("tipo", "versao")
    search_fields = ("user__email",)
    readonly_fields = ("user", "tipo", "versao", "ip", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "nome", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "nome")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Pessoal", {"fields": ("nome", "telefone", "role")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nome", "role", "password1", "password2"),
            },
        ),
    )
