from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Consent, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("username",)
    list_display = ("username", "nome", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "nome", "email")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Pessoal", {"fields": ("nome", "email", "telefone", "role")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "nome", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "tipo", "versao", "created_at", "ip")
    list_filter = ("tipo", "versao")
    search_fields = ("user__nome", "user__username")
    readonly_fields = ("user", "tipo", "versao", "ip", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False
