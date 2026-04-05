import uuid
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Pedido, PedidoDetalle, Pago, Comprobante
from .serializers import (
    PedidoListSerializer, PedidoDetalladoSerializer,
    CrearPedidoSerializer
)
from usuarios.models import Usuario
from catalogo.models import Producto, ProductoVariante


class PedidoViewSet(ReadOnlyModelViewSet):
    """
    GET /api/ventas/pedidos/?uid=<firebase_uid>        → lista de pedidos del usuario
    GET /api/ventas/pedidos/{id}/?uid=<firebase_uid>   → detalle de un pedido
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        uid = self.request.query_params.get('uid')
        if uid:
            return Pedido.objects.filter(
                usuario__firebase_uid=uid
            ).select_related('usuario').prefetch_related(
                'detalles', 'pago', 'comprobante'
            )
        return Pedido.objects.none()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PedidoDetalladoSerializer
        return PedidoListSerializer


class CrearPedidoView(APIView):
    """
    POST /api/ventas/pedidos/crear/
    Crea un pedido completo con sus detalles, descuenta stock,
    registra el pago pendiente y genera el comprobante.

    Body JSON:
    {
        "uid": "firebase_uid_del_cliente",
        "metodo_entrega": "recojo|delivery|courier",
        "costo_envio": 5.00,
        "descuento": 0,
        "tipo_comprobante": "boleta|factura",
        "observacion": "...",
        "items": [
            {"producto_id": 1, "variante_id": 2, "cantidad": 3}
        ]
    }
    """
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = CrearPedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            usuario = Usuario.objects.get(firebase_uid=data['uid'])
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        subtotal = Decimal('0')
        items_validados = []

        for item in data['items']:
            try:
                producto = Producto.objects.get(id=item['producto_id'], activo=True)
            except Producto.DoesNotExist:
                return Response({'error': f"Producto {item['producto_id']} no encontrado"}, status=400)

            variante = None
            precio = producto.precio_base

            if item.get('variante_id'):
                try:
                    variante = ProductoVariante.objects.get(
                        id=item['variante_id'], producto=producto, activo=True
                    )
                    precio = variante.precio
                    if variante.stock < item['cantidad']:
                        return Response(
                            {'error': f"Stock insuficiente para {producto.nombre} — {variante.nombre_variante}"},
                            status=400
                        )
                    variante.stock -= item['cantidad']
                    variante.save()
                except ProductoVariante.DoesNotExist:
                    return Response({'error': f"Variante no encontrada"}, status=400)

            item_subtotal = precio * item['cantidad']
            subtotal += item_subtotal
            items_validados.append({
                'producto': producto,
                'variante': variante,
                'cantidad': item['cantidad'],
                'precio_unitario': precio,
                'subtotal': item_subtotal,
            })

        descuento = data.get('descuento', Decimal('0'))
        costo_envio = data.get('costo_envio', Decimal('0'))
        total = subtotal - descuento + costo_envio

        codigo = f"YAL-{uuid.uuid4().hex[:8].upper()}"

        pedido = Pedido.objects.create(
            usuario=usuario,
            codigo=codigo,
            estado='pendiente',
            subtotal=subtotal,
            descuento=descuento,
            costo_envio=costo_envio,
            total=total,
            metodo_entrega=data['metodo_entrega'],
            observacion=data.get('observacion', ''),
        )

        for item in items_validados:
            PedidoDetalle.objects.create(
                pedido=pedido,
                producto=item['producto'],
                variante=item['variante'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario'],
                subtotal=item['subtotal'],
            )

        Pago.objects.create(
            pedido=pedido,
            metodo_pago='culqi',
            estado='pendiente',
            monto=total,
        )

        Comprobante.objects.create(
            pedido=pedido,
            tipo=data['tipo_comprobante'],
            serie='B001' if data['tipo_comprobante'] == 'boleta' else 'F001',
            numero=str(pedido.id).zfill(8),
            estado_sunat='pendiente',
        )

        return Response(
            PedidoDetalladoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )
