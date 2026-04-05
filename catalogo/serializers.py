from rest_framework import serializers
from .models import Categoria, Marca, Producto, ProductoVariante, ImagenProducto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo']


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre', 'activo']


class ImagenProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen_url', 'orden', 'es_principal']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class ProductoVarianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoVariante
        fields = ['id', 'nombre_variante', 'precio', 'stock', 'sku', 'activo']


class ProductoListSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    imagen_principal = serializers.SerializerMethodField()
    tiene_stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_publicacion',
            'precio_base', 'activo', 'permite_mayor',
            'categoria_nombre', 'marca_nombre',
            'imagen_principal', 'tiene_stock'
        ]

    def get_imagen_principal(self, obj):
        request = self.context.get('request')
        img = obj.imagenes.filter(es_principal=True).first()
        if img and request:
            return request.build_absolute_uri(img.imagen.url)
        return None

    def get_tiene_stock(self, obj):
        return obj.variantes.filter(stock__gt=0, activo=True).exists()


class ProductoDetalleSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    variantes = ProductoVarianteSerializer(many=True, read_only=True)
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    tiene_stock = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_publicacion',
            'precio_base', 'activo', 'permite_mayor', 'stock_minimo',
            'categoria', 'marca', 'variantes', 'imagenes',
            'tiene_stock', 'creado_en'
        ]

    def get_tiene_stock(self, obj):
        return obj.variantes.filter(stock__gt=0, activo=True).exists()
