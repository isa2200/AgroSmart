#!/usr/bin/env python
"""
Script para actualizar permisos de usuarios existentes.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.usuarios.models import PerfilUsuario
from apps.aves.models import LoteAves

def actualizar_permisos():
    """Actualiza los permisos de todos los usuarios según su rol."""
    
    print("Iniciando actualización de permisos...")
    
    # Obtener el ContentType para LoteAves
    content_type = ContentType.objects.get_for_model(LoteAves)
    
    # Crear permisos si no existen
    permisos_lote = [
        ('add_loteaves', 'Can add lote aves'),
        ('change_loteaves', 'Can change lote aves'),
        ('delete_loteaves', 'Can delete lote aves'),
        ('view_loteaves', 'Can view lote aves'),
    ]
    
    for codename, name in permisos_lote:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={'name': name}
        )
        if created:
            print(f"Permiso creado: {name}")
    
    # Actualizar usuarios
    usuarios_actualizados = 0
    
    for perfil in PerfilUsuario.objects.all():
        user = perfil.user
        print(f"\nActualizando usuario: {user.username} (rol: {perfil.rol})")
        
        # Limpiar grupos existentes
        user.groups.clear()
        
        if perfil.rol == 'superusuario':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"  - Configurado como superusuario")
            
        elif perfil.rol == 'admin_aves':
            # Crear grupo para admin_aves
            group, created = Group.objects.get_or_create(name='Administradores_Aves')
            if created:
                print(f"  - Grupo creado: Administradores_Aves")
            
            # Asignar todos los permisos de LoteAves
            for codename, _ in permisos_lote:
                permission = Permission.objects.get(
                    codename=codename,
                    content_type=content_type
                )
                group.permissions.add(permission)
                print(f"  - Permiso agregado al grupo: {codename}")
            
            user.groups.add(group)
            print(f"  - Usuario agregado al grupo: Administradores_Aves")
            
        elif perfil.rol == 'solo_vista':
            # Crear grupo para solo_vista
            group, created = Group.objects.get_or_create(name='Solo_Vista')
            if created:
                print(f"  - Grupo creado: Solo_Vista")
            
            # Solo permiso de vista
            permission = Permission.objects.get(
                codename='view_loteaves',
                content_type=content_type
            )
            group.permissions.add(permission)
            user.groups.add(group)
            print(f"  - Permiso de vista agregado")
            
        usuarios_actualizados += 1
    
    print(f"\n✅ Actualización completada. {usuarios_actualizados} usuarios procesados.")
    
    # Mostrar resumen de permisos por usuario
    print("\n📋 RESUMEN DE PERMISOS:")
    for perfil in PerfilUsuario.objects.all():
        user = perfil.user
        permisos = user.get_all_permissions()
        permisos_lote = [p for p in permisos if 'loteaves' in p]
        print(f"\n👤 {user.username} ({perfil.rol}):")
        if user.is_superuser:
            print("  - SUPERUSUARIO (todos los permisos)")
        else:
            for permiso in permisos_lote:
                print(f"  - {permiso}")
            if not permisos_lote:
                print("  - Sin permisos específicos de lotes")

if __name__ == '__main__':
    actualizar_permisos()