"""
Comando para crear un usuario administrador de aves.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario
from datetime import date


class Command(BaseCommand):
    help = 'Crea un usuario administrador de aves para pruebas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin_aves',
            help='Nombre de usuario (por defecto: admin_aves)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña (por defecto: admin123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin_aves@agrosmart.com',
            help='Email del usuario'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario {username} ya existe.')
            )
            return

        # Crear el usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Aves',
            is_staff=False
        )

        # Crear el perfil con rol admin_aves
        perfil = PerfilUsuario.objects.create(
            user=user,
            rol='admin_aves',
            telefono='3001234567',
            cedula='12345678',
            direccion='Granja AgroSmart',
            acceso_modulo_avicola=True,
            puede_eliminar_registros=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Usuario {username} creado exitosamente con rol admin_aves.\n'
                f'Credenciales:\n'
                f'  Usuario: {username}\n'
                f'  Contraseña: {password}\n'
                f'  Email: {email}'
            )
        )