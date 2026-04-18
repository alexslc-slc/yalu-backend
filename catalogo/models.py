from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"


class Producto(models.Model):
    TIPO_CHOICES = [
        ("producto", "Producto"),
        ("paquete", "Paquete"),
        ("servicio", "Servicio"),
    ]
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_publicacion = models.CharField(max_length=20, choices=TIPO_CHOICES, default="producto")
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    permite_mayor = models.BooleanField(default=False)
    stock_minimo = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class ProductoVariante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="variantes")
    nombre_variante = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.producto.nombre} — {self.nombre_variante}"

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="productos/")
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"
        ordering = ["orden"]