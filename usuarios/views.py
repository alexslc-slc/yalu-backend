from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Rol, Usuario, Direccion
from .serializers import UsuarioSerializer, DireccionSerializer, FirebaseLoginSerializer

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth, credentials
    FIREBASE_DISPONIBLE = True
except ImportError:
    FIREBASE_DISPONIBLE = False


class FirebaseLoginView(APIView):
    """
    POST /api/usuarios/login/
    Recibe el token de Firebase, verifica con Firebase Admin SDK,
    crea o actualiza el usuario local y devuelve los datos del perfil.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FirebaseLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['firebase_token']

        if not FIREBASE_DISPONIBLE:
            return Response(
                {'error': 'Firebase no configurado en el servidor'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            decoded = firebase_auth.verify_id_token(token)
        except Exception:
            return Response(
                {'error': 'Token inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        uid = decoded.get('uid')
        email = decoded.get('email', '')
        nombre = decoded.get('name', '')
        partes = nombre.split(' ', 1)
        nombres = partes[0] if partes else ''
        apellidos = partes[1] if len(partes) > 1 else ''

        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')

        usuario, creado = Usuario.objects.get_or_create(
            firebase_uid=uid,
            defaults={
                'email': email,
                'nombres': nombres,
                'apellidos': apellidos,
                'rol': rol_cliente,
            }
        )

        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'creado': creado
        }, status=status.HTTP_200_OK)


class PerfilView(APIView):
    """
    GET /api/usuarios/perfil/?uid=<firebase_uid>
    Devuelve el perfil completo del usuario con sus direcciones.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.query_params.get('uid')
        if not uid:
            return Response({'error': 'Se requiere uid'}, status=400)
        try:
            usuario = Usuario.objects.get(firebase_uid=uid)
            return Response(UsuarioSerializer(usuario).data)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)


class DireccionViewSet(ModelViewSet):
    """
    GET/POST/PUT/DELETE /api/usuarios/direcciones/?uid=<firebase_uid>
    """
    serializer_class = DireccionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        uid = self.request.query_params.get('uid')
        if uid:
            return Direccion.objects.filter(usuario__firebase_uid=uid)
        return Direccion.objects.none()

    def perform_create(self, serializer):
        uid = self.request.query_params.get('uid')
        usuario = Usuario.objects.get(firebase_uid=uid)
        serializer.save(usuario=usuario)
