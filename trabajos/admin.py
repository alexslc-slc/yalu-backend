from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import TrabajoManual, TrabajoManualFoto


class FotoInline(TabularInline):
    model = TrabajoManualFoto
    extra = 1


@admin.register(TrabajoManual)
class TrabajoManualAdmin(ModelAdmin):
    list_display = ["titulo", "estado", "precio_estimado", "precio_final", "created_at"]
    list_filter = ["estado"]
    search_fields = ["titulo", "descripcion"]
    inlines = [FotoInline]


@admin.register(TrabajoManualFoto)
class TrabajoManualFotoAdmin(ModelAdmin):
    list_display = ["trabajo", "orden"]
    search_fields = ["trabajo__titulo"]