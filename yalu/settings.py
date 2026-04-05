from django.urls import reverse_lazy
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-v#5o&&u%j3@#dw7m6m8fnqp3@pw)*9cpb^%a_1)4j^7$e47m9_'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "usuarios",
    "catalogo",
    "ventas",
    "trabajos",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'yalu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'yalu.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================
# UNFOLD (CORRECTO)
# ========================
UNFOLD = {
    "SITE_TITLE": "Yalú Admin",
    "SITE_HEADER": "Librería Bazar Yalú",
    "SITE_SUBHEADER": "Panel de administración",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SITE_SYMBOL": "storefront",
    "COLORS": {
        "primary": {
            "50": "255 247 237",
            "100": "255 237 213",
            "200": "254 215 170",
            "300": "253 186 116",
            "400": "251 146 60",
            "500": "249 115 22",
            "600": "234 88 12",
            "700": "194 65 12",
            "800": "154 52 18",
            "900": "124 45 18",
            "950": "67 20 7",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Catálogo",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Productos",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:catalogo_producto_changelist"),
                    },
                    {
                        "title": "Categorías",
                        "icon": "category",
                        "link": reverse_lazy("admin:catalogo_categoria_changelist"),
                    },
                    {
                        "title": "Marcas",
                        "icon": "sell",
                        "link": reverse_lazy("admin:catalogo_marca_changelist"),
                    },
                ],
            },
            {
                "title": "Ventas",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Pedidos",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:ventas_pedido_changelist"),
                    },
                    {
                        "title": "Pagos",
                        "icon": "payments",
                        "link": reverse_lazy("admin:ventas_pago_changelist"),
                    },
                    {
                        "title": "Comprobantes",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:ventas_comprobante_changelist"),
                    },
                ],
            },
            {
                "title": "Trabajos Manuales",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Proyectos",
                        "icon": "brush",
                        "link": reverse_lazy("admin:trabajos_trabajomanual_changelist"),
                    },
                    {
                        "title": "Fotos",
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:trabajos_trabajomanualfoto_changelist"),
                    },
                ],
            },
            {
                "title": "Usuarios",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Usuarios",
                        "icon": "person",
                        "link": reverse_lazy("admin:usuarios_usuario_changelist"),
                    },
                    {
                        "title": "Roles",
                        "icon": "shield",
                        "link": reverse_lazy("admin:usuarios_rol_changelist"),
                    },
                    {
                        "title": "Direcciones",
                        "icon": "map",
                        "link": reverse_lazy("admin:usuarios_direccion_changelist"),
                    },
                ],
            },
            {
                "title": "Autenticación",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Grupos",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

CORS_ALLOW_ALL_ORIGINS = True  # solo desarrollo

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}