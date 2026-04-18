# trabajos/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import TrabajoManual
from .serializers import TrabajoManualSerializer


class TrabajoManualViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/trabajos/          → lista de trabajos para la galería
    GET /api/trabajos/{id}/     → detalle de un trabajo con fotos
    """
    queryset = TrabajoManual.objects.prefetch_related('fotos').order_by('-created_at')
    serializer_class = TrabajoManualSerializer
    permission_classes = [AllowAny]
