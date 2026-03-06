
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario
import uuid

class Command(BaseCommand):
    help = 'Crea usuarios iniciales para cada rol del sistema'

    def handle(self, *args, **kwargs):
        roles_data = [
            ('superusuario', 'admin'),
            ('admin_aves', 'admin_aves'),
            ('admin_bovinos', 'admin_bovinos'),
            ('admin_equinos', 'admin_equinos'),
            ('admin_porcinos', 'admin_porcinos'),
            ('admin_ovinos', 'admin_ovinos'),
            ('admin_caprinos', 'admin_caprinos'),
            ('admin_cunicola', 'admin_cunicola'),
            ('veterinario', 'veterinario'),
            ('solo_vista', 'visitante'),
        ]

        password = 'AgroSmart2026!'

        for rol, username in roles_data:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.first_name = rol.replace('admin_', 'Admin ').replace('_', ' ').title()
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Usuario "{username}" creado'))
            else:
                self.stdout.write(self.style.WARNING(f'Usuario "{username}" ya existe'))

            # Obtener o crear perfil
            try:
                perfil = user.perfilusuario
            except PerfilUsuario.DoesNotExist:
                perfil = PerfilUsuario.objects.create(
                    user=user,
                    rol=rol,
                    cedula=f'CED-{username}'
                )
            
            # Actualizar rol
            perfil.rol = rol
            if not perfil.cedula or perfil.cedula.startswith('temp_'):
                perfil.cedula = f'CED-{username}'
            perfil.save()
            
            self.stdout.write(self.style.SUCCESS(f'Perfil actualizado para "{username}" con rol "{rol}"'))

        self.stdout.write(self.style.SUCCESS('Proceso completado'))
