

from django.db import models
from usuarios.models import Usuario


class TrabajoManual(models.Model):
    ESTADO_CHOICES = [
        ("consulta", "Consulta recibida"),
        ("cotizado", "Cotizado"),
        ("en_proceso", "En proceso"),
        ("entregado", "Entregado"),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="consulta")
    whatsapp_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Trabajo Manual"
        verbose_name_plural = "Trabajos Manuales"


class TrabajoManualFoto(models.Model):
    trabajo = models.ForeignKey(TrabajoManual, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="trabajos/")
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Foto {self.orden} de {self.trabajo.titulo}"

    class Meta:
        verbose_name = "Foto de trabajo"
        verbose_name_plural = "Fotos de trabajo"
        ordering = ["orden"]