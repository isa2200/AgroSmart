from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario, RegistroAcceso


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'perfilusuario__rol')
    
    def get_rol(self, obj):
        try:
            return obj.perfilusuario.get_rol_display()
        except:
            return 'Sin perfil'
    get_rol.short_description = 'Rol'


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'modulo', 'ip_address', 'created_at']
    list_filter = ['accion', 'modulo', 'created_at']
    search_fields = ['usuario__username', 'accion', 'ip_address']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)