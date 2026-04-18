from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Categoria, Marca, Producto
from .serializers import (
    CategoriaSerializer, MarcaSerializer,
    ProductoListSerializer, ProductoDetalleSerializer
)


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.filter(activo=True)
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]


class MarcaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Marca.objects.filter(activo=True)
    serializer_class = MarcaSerializer
    permission_classes = [AllowAny]


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'marca', 'tipo_publicacion', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio_base', 'creado_en', 'nombre']
    ordering = ['nombre']

    def get_queryset(self):
        return Producto.objects.filter(activo=True).select_related(
            'categoria', 'marca'
        ).prefetch_related('variantes', 'imagenes')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetalleSerializer
        return ProductoListSerializer
