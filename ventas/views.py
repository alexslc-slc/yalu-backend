import uuid
import requests as http_requests
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
from .models import Pedido, PedidoDetalle, Pago, Comprobante
from .serializers import (
    PedidoListSerializer, PedidoDetalladoSerializer,
    CrearPedidoSerializer
)
from usuarios.models import Usuario
from catalogo.models import Producto, ProductoVariante


class PedidoViewSet(ReadOnlyModelViewSet):
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
            precio = producto.precio  # ← corregido

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
                    return Response({'error': 'Variante no encontrada'}, status=400)

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


class CrearPedidoInvitadoView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        captcha_token = request.data.get('captcha_token')
        if not captcha_token:
            return Response({'error': 'CAPTCHA requerido'}, status=400)

        captcha_resp = http_requests.post('https://hcaptcha.com/siteverify', data={
            'secret': settings.HCAPTCHA_SECRET,
            'response': captcha_token,
        })
        if not captcha_resp.json().get('success'):
            return Response({'error': 'CAPTCHA inválido'}, status=400)

        nombre = request.data.get('nombre', '').strip()
        dni = request.data.get('dni', '').strip()
        correo = request.data.get('correo', '').strip()
        items = request.data.get('items', [])

        if not nombre or not dni or not correo or not items:
            return Response({'error': 'Faltan campos requeridos'}, status=400)

        subtotal = Decimal('0')
        items_validados = []

        for item in items:
            try:
                producto = Producto.objects.get(id=item['producto_id'], activo=True)
            except Producto.DoesNotExist:
                return Response({'error': f"Producto {item['producto_id']} no encontrado"}, status=400)

            variante = None
            precio = producto.precio  # ← corregido

            if item.get('variante_id'):
                try:
                    variante = ProductoVariante.objects.get(
                        id=item['variante_id'], producto=producto, activo=True
                    )
                    precio = variante.precio
                    if variante.stock < item['cantidad']:
                        return Response(
                            {'error': f"Stock insuficiente para {producto.nombre}"},
                            status=400
                        )
                    variante.stock -= item['cantidad']
                    variante.save()
                except ProductoVariante.DoesNotExist:
                    return Response({'error': 'Variante no encontrada'}, status=400)

            item_subtotal = precio * item['cantidad']
            subtotal += item_subtotal
            items_validados.append({
                'producto': producto,
                'variante': variante,
                'cantidad': item['cantidad'],
                'precio_unitario': precio,
                'subtotal': item_subtotal,
            })

        costo_envio = Decimal(str(request.data.get('costo_envio', '0')))
        total = subtotal + costo_envio
        codigo = f"YAL-INV-{uuid.uuid4().hex[:8].upper()}"

        pedido = Pedido.objects.create(
            usuario=None,
            cliente_nombre=nombre,
            cliente_dni=dni,
            cliente_correo=correo,
            codigo=codigo,
            estado='pendiente',
            subtotal=subtotal,
            descuento=Decimal('0'),
            costo_envio=costo_envio,
            total=total,
            metodo_entrega=request.data.get('metodo_entrega', 'courier'),
            observacion=request.data.get('observacion', ''),
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

        tipo_comprobante = request.data.get('tipo_comprobante', 'boleta')
        Comprobante.objects.create(
            pedido=pedido,
            tipo=tipo_comprobante,
            serie='B001' if tipo_comprobante == 'boleta' else 'F001',
            numero=str(pedido.id).zfill(8),
            estado_sunat='pendiente',
        )

        return Response({'codigo': pedido.codigo, 'total': str(total)}, status=201)