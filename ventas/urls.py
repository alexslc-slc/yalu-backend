from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, CrearPedidoView

router = DefaultRouter()
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('pedidos/crear/', CrearPedidoView.as_view(), name='crear-pedido'),
] + router.urls
