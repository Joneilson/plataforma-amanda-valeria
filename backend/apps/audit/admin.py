from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "user", "ip", "resource", "resource_id")
    list_filter = ("action", "created_at")
    search_fields = ("user__email", "ip", "resource", "resource_id")
    readonly_fields = ("user", "action", "resource", "resource_id", "ip", "user_agent", "metadata", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
