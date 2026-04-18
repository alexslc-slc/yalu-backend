# trabajos/serializers.py
from rest_framework import serializers
from .models import TrabajoManual, TrabajoManualFoto


class TrabajoFotoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = TrabajoManualFoto
        fields = ['id', 'imagen_url', 'orden']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class TrabajoManualSerializer(serializers.ModelSerializer):
    fotos = TrabajoFotoSerializer(many=True, read_only=True)

    class Meta:
        model = TrabajoManual
        fields = [
            'id', 'titulo', 'descripcion',
            'precio_estimado', 'estado',
            'whatsapp_link', 'fotos', 'created_at'
        ]
