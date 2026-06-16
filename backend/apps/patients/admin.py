from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "inicio_tratamento", "valor_sessao")
    list_filter = ("status",)
    search_fields = ("user__nome", "user__email")
    autocomplete_fields = ("user",)
