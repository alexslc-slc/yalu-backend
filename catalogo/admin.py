from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Categoria, Marca, Producto, ProductoVariante, ImagenProducto


class VarianteInline(TabularInline):
    model = ProductoVariante
    extra = 1


class ImagenInline(TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Marca)
class MarcaAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Producto)
class ProductoAdmin(ModelAdmin):
    list_display = ["nombre", "categoria", "marca", "precio_base", "tipo_publicacion", "activo", "permite_mayor"]
    list_filter = ["categoria", "marca", "activo", "tipo_publicacion"]
    search_fields = ["nombre", "descripcion"]
    inlines = [VarianteInline, ImagenInline]