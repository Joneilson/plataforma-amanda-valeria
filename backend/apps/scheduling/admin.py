from django.contrib import admin

from .models import Appointment, Availability


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "hora_inicio", "hora_fim", "modalidade", "ativo")
    list_filter = ("dia_semana", "modalidade", "ativo")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "data_hora", "duracao_min", "modalidade", "status", "valor")
    list_filter = ("status", "modalidade", "data_hora")
    search_fields = ("patient__user__nome",)
    date_hierarchy = "data_hora"
    autocomplete_fields = ("patient",)
