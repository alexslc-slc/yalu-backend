from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/catalogo/',  include('catalogo.urls')),
    path('api/usuarios/',  include('usuarios.urls')),
    path('api/ventas/',    include('ventas.urls')),
    path('api/trabajos/',  include('trabajos.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)