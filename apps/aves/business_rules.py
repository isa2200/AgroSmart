"""
Reglas de negocio específicas para el módulo avícola
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    LoteAves, BitacoraDiaria, MovimientoHuevos, AlertaSistema,
    InventarioConcentrado, ConsumoConcentrado, RegistroVacunacion
)
from .validators import ValidadorAvicola, ReglaDespachoHuevos

class GestorLoteAves:
    """
    Gestor de reglas de negocio para lotes de aves
    """
    
    @staticmethod
    @transaction.atomic
    def crear_lote(datos_lote):
        """
        Crea un nuevo lote aplicando todas las reglas de negocio
        """
        # Validar capacidad del galpón
        galpon = datos_lote['galpon']
        if galpon.lotes_activos().count() >= galpon.capacidad_maxima_lotes:
            raise ValueError(f"El galpón {galpon.nombre} ha alcanzado su capacidad máxima de lotes")
        
        # Validar que no exceda la capacidad de aves del galpón
        aves_actuales = sum(lote.cantidad_actual for lote in galpon.lotes_activos())
        if aves_actuales + datos_lote['cantidad_inicial'] > galpon.capacidad_aves:
            raise ValueError(
                f"El galpón no tiene capacidad suficiente. "
                f"Disponible: {galpon.capacidad_aves - aves_actuales}, "
                f"Solicitado: {datos_lote['cantidad_inicial']}"
            )
        
        # Crear el lote
        lote = LoteAves.objects.create(**datos_lote)
        
        # Crear alerta de bienvenida
        AlertaSistema.objects.create(
            tipo='nuevo_lote',
            mensaje=f"Nuevo lote {lote.codigo} ingresado con {lote.cantidad_inicial} aves",
            lote=lote,
            fecha=lote.fecha_ingreso,
            prioridad='informativa'
        )
        
        return lote
    
    @staticmethod
    @transaction.atomic
    def finalizar_lote(lote, fecha_finalizacion, motivo):
        """
        Finaliza un lote aplicando todas las reglas necesarias
        """
        # Validar que no tenga movimientos pendientes
        movimientos_pendientes = MovimientoHuevos.objects.filter(
            lote=lote,
            cantidad_disponible__gt=0
        )
        
        if movimientos_pendientes.exists():
            raise ValueError("No se puede finalizar el lote con movimientos de huevos pendientes")
        
        # Actualizar estado del lote
        lote.estado = 'finalizado'
        lote.fecha_finalizacion = fecha_finalizacion
        lote.motivo_finalizacion = motivo
        lote.save()
        
        # Crear registro de finalización
        AlertaSistema.objects.create(
            tipo='lote_finalizado',
            mensaje=f"Lote {lote.codigo} finalizado. Motivo: {motivo}",
            lote=lote,
            fecha=fecha_finalizacion,
            prioridad='informativa'
        )
        
        return lote

class GestorProduccion:
    """
    Gestor de reglas de negocio para producción de huevos
    """
    
    @staticmethod
    @transaction.atomic
    def registrar_produccion_diaria(lote, fecha, datos_produccion):
        """
        Registra la producción diaria aplicando todas las validaciones
        """
        # Validar datos de entrada
        ValidadorAvicola.validar_fecha_registro(fecha, lote)
        ValidadorAvicola.validar_produccion_huevos(
            lote, 
            datos_produccion['huevos_buenos'],
            datos_produccion['huevos_rotos'],
            datos_produccion['huevos_sucios'],
            fecha
        )
        
        if datos_produccion.get('mortalidad', 0) > 0:
            ValidadorAvicola.validar_mortalidad(lote, datos_produccion['mortalidad'], fecha)
        
        # Verificar si ya existe registro para esta fecha
        bitacora, creada = BitacoraDiaria.objects.get_or_create(
            lote=lote,
            fecha=fecha,
            defaults=datos_produccion
        )
        
        if not creada:
            # Actualizar registro existente
            for campo, valor in datos_produccion.items():
                setattr(bitacora, campo, valor)
            bitacora.save()
        
        # Aplicar reglas automáticas
        GestorProduccion._aplicar_reglas_produccion(bitacora)
        
        # Crear movimientos de huevos automáticamente
        if datos_produccion['huevos_buenos'] > 0:
            MovimientoHuevos.objects.create(
                lote=lote,
                tipo_movimiento='entrada',
                categoria=datos_produccion.get('categoria_huevo'),
                cantidad=datos_produccion['huevos_buenos'],
                cantidad_disponible=datos_produccion['huevos_buenos'],
                fecha=fecha,
                origen='produccion',
                observaciones=f'Producción diaria lote {lote.codigo}'
            )
        
        return bitacora
    
    @staticmethod
    def _aplicar_reglas_produccion(bitacora):
        """
        Aplica reglas automáticas después del registro de producción
        """
        lote = bitacora.lote
        
        # Actualizar cantidad de aves si hay mortalidad
        if bitacora.mortalidad > 0:
            cantidad_anterior = lote.cantidad_actual
            lote.cantidad_actual -= bitacora.mortalidad
            lote.save()
            
            # Crear alerta si la mortalidad es alta
            porcentaje_mortalidad = (bitacora.mortalidad / cantidad_anterior) * 100
            if porcentaje_mortalidad > 2:
                AlertaSistema.objects.create(
                    tipo='mortalidad_alta',
                    mensaje=f"Mortalidad alta: {porcentaje_mortalidad:.1f}% en lote {lote.codigo}",
                    lote=lote,
                    fecha=bitacora.fecha,
                    prioridad='alta'
                )
        
        # Calcular y alertar sobre baja producción
        total_huevos = bitacora.huevos_buenos + bitacora.huevos_rotos + bitacora.huevos_sucios
        if total_huevos > 0:
            porcentaje_postura = (total_huevos / lote.cantidad_actual) * 100
            
            # Alerta si la postura es menor al 70%
            if porcentaje_postura < 70:
                AlertaSistema.objects.create(
                    tipo='baja_produccion',
                    mensaje=f"Baja producción: {porcentaje_postura:.1f}% en lote {lote.codigo}",
                    lote=lote,
                    fecha=bitacora.fecha,
                    prioridad='media'
                )
        
        # Alerta por alta proporción de huevos defectuosos
        if total_huevos > 0:
            porcentaje_defectuosos = ((bitacora.huevos_rotos + bitacora.huevos_sucios) / total_huevos) * 100
            if porcentaje_defectuosos > 20:
                AlertaSistema.objects.create(
                    tipo='huevos_defectuosos',
                    mensaje=f"Alto porcentaje de huevos defectuosos: {porcentaje_defectuosos:.1f}% en lote {lote.codigo}",
                    lote=lote,
                    fecha=bitacora.fecha,
                    prioridad='media'
                )

class GestorMovimientoHuevos:
    """
    Gestor de reglas de negocio para movimientos de huevos
    """
    
    @staticmethod
    @transaction.atomic
    def despachar_huevos(categoria, cantidad, destino, fecha_despacho, observaciones=""):
        """
        Despacha huevos aplicando reglas FIFO y validaciones
        """
        # Validar disponibilidad
        disponible = MovimientoHuevos.objects.filter(
            categoria=categoria,
            cantidad_disponible__gt=0
        ).aggregate(total=models.Sum('cantidad_disponible'))['total'] or 0
        
        if disponible < cantidad:
            raise ValueError(f"No hay suficientes huevos disponibles. Disponible: {disponible}, Solicitado: {cantidad}")
        
        # Aplicar FIFO - obtener lotes más antiguos primero
        lotes_disponibles = MovimientoHuevos.objects.filter(
            categoria=categoria,
            cantidad_disponible__gt=0,
            tipo_movimiento='entrada'
        ).order_by('fecha')
        
        cantidad_restante = cantidad
        movimientos_despacho = []
        
        for lote_huevos in lotes_disponibles:
            if cantidad_restante <= 0:
                break
            
            # Validar frescura
            resultado_frescura = ReglaDespachoHuevos.validar_frescura_huevos(
                lote_huevos.fecha, fecha_despacho
            )
            
            if 'advertencia' in resultado_frescura:
                # Crear alerta de advertencia pero continuar
                AlertaSistema.objects.create(
                    tipo='huevos_antiguos',
                    mensaje=resultado_frescura['advertencia'],
                    lote=lote_huevos.lote,
                    fecha=fecha_despacho,
                    prioridad='baja'
                )
            
            # Determinar cantidad a tomar de este lote
            cantidad_a_tomar = min(cantidad_restante, lote_huevos.cantidad_disponible)
            
            # Actualizar disponibilidad
            lote_huevos.cantidad_disponible -= cantidad_a_tomar
            lote_huevos.save()
            
            # Crear movimiento de salida
            movimiento_salida = MovimientoHuevos.objects.create(
                lote=lote_huevos.lote,
                tipo_movimiento='salida',
                categoria=categoria,
                cantidad=cantidad_a_tomar,
                cantidad_disponible=0,
                fecha=fecha_despacho,
                destino=destino,
                observaciones=f"Despacho - {observaciones}",
                movimiento_origen=lote_huevos
            )
            
            movimientos_despacho.append(movimiento_salida)
            cantidad_restante -= cantidad_a_tomar
        
        return movimientos_despacho
    
    @staticmethod
    def calcular_inventario_actual():
        """
        Calcula el inventario actual de huevos por categoría
        """
        from django.db.models import Sum
        
        inventario = MovimientoHuevos.objects.filter(
            cantidad_disponible__gt=0
        ).values('categoria__nombre').annotate(
            total=Sum('cantidad_disponible')
        ).order_by('categoria__nombre')
        
        return list(inventario)

class GestorConcentrado:
    """
    Gestor de reglas de negocio para concentrados
    """
    
    @staticmethod
    @transaction.atomic
    def registrar_consumo(lote, tipo_concentrado, cantidad_kg, fecha):
        """
        Registra el consumo de concentrado con validaciones
        """
        # Validar consumo
        ValidadorAvicola.validar_consumo_concentrado(lote, cantidad_kg, fecha)
        
        # Verificar disponibilidad en inventario
        inventario = InventarioConcentrado.objects.filter(
            tipo_concentrado=tipo_concentrado,
            cantidad_disponible__gt=0
        ).order_by('fecha_vencimiento')
        
        disponible = sum(inv.cantidad_disponible for inv in inventario)
        if disponible < cantidad_kg:
            raise ValueError(f"No hay suficiente concentrado disponible. Disponible: {disponible}kg")
        
        # Aplicar FIFO para el consumo
        cantidad_restante = cantidad_kg
        consumos = []
        
        for inv in inventario:
            if cantidad_restante <= 0:
                break
            
            cantidad_a_consumir = min(cantidad_restante, inv.cantidad_disponible)
            
            # Actualizar inventario
            inv.cantidad_disponible -= cantidad_a_consumir
            inv.save()
            
            # Crear registro de consumo
            consumo = ConsumoConcentrado.objects.create(
                lote=lote,
                tipo_concentrado=tipo_concentrado,
                cantidad_kg=cantidad_a_consumir,
                fecha=fecha,
                inventario_origen=inv
            )
            
            consumos.append(consumo)
            cantidad_restante -= cantidad_a_consumir
        
        # Crear alerta si el inventario está bajo
        GestorConcentrado._verificar_stock_bajo(tipo_concentrado)
        
        return consumos
    
    @staticmethod
    def _verificar_stock_bajo(tipo_concentrado):
        """
        Verifica si el stock está bajo y crea alertas
        """
        stock_actual = InventarioConcentrado.objects.filter(
            tipo_concentrado=tipo_concentrado,
            cantidad_disponible__gt=0
        ).aggregate(total=models.Sum('cantidad_disponible'))['total'] or 0
        
        # Alerta si queda menos de 500kg
        if stock_actual < 500:
            AlertaSistema.objects.create(
                tipo='stock_bajo',
                mensaje=f"Stock bajo de {tipo_concentrado.nombre}: {stock_actual}kg disponibles",
                fecha=timezone.now().date(),
                prioridad='media'
            )

class GestorVacunacion:
    """
    Gestor de reglas de negocio para vacunación
    """
    
    @staticmethod
    @transaction.atomic
    def aplicar_vacuna(lote, plan_vacunacion, fecha_aplicacion, observaciones=""):
        """
        Aplica una vacuna según el plan establecido
        """
        # Validar que el plan esté activo
        if not plan_vacunacion.activo:
            raise ValueError("El plan de vacunación no está activo")
        
        # Validar fecha de aplicación
        if fecha_aplicacion < plan_vacunacion.fecha_inicio:
            raise ValueError("La fecha de aplicación es anterior al inicio del plan")
        
        # Crear registro de vacunación
        registro = RegistroVacunacion.objects.create(
            lote=lote,
            plan_vacunacion=plan_vacunacion,
            vacuna=plan_vacunacion.vacuna,
            fecha_aplicacion=fecha_aplicacion,
            dosis_aplicada=plan_vacunacion.dosis_por_ave * lote.cantidad_actual,
            aves_vacunadas=lote.cantidad_actual,
            observaciones=observaciones
        )
        
        # Crear alerta informativa
        AlertaSistema.objects.create(
            tipo='vacunacion_aplicada',
            mensaje=f"Vacuna {plan_vacunacion.vacuna.nombre} aplicada a lote {lote.codigo}",
            lote=lote,
            fecha=fecha_aplicacion,
            prioridad='informativa'
        )
        
        return registro
    
    @staticmethod
    def verificar_vacunas_pendientes():
        """
        Verifica vacunas que deben aplicarse pronto y crea alertas
        """
        from django.db.models import Q
        
        fecha_limite = timezone.now().date() + timedelta(days=7)
        
        planes_pendientes = PlanVacunacion.objects.filter(
            activo=True,
            fecha_aplicacion__lte=fecha_limite
        ).exclude(
            registrovacunacion__fecha_aplicacion__isnull=False
        )
        
        for plan in planes_pendientes:
            dias_restantes = (plan.fecha_aplicacion - timezone.now().date()).days
            
            AlertaSistema.objects.get_or_create(
                tipo='vacuna_pendiente',
                lote=plan.lote,
                fecha=timezone.now().date(),
                defaults={
                    'mensaje': f"Vacuna {plan.vacuna.nombre} debe aplicarse en {dias_restantes} días",
                    'prioridad': 'alta' if dias_restantes <= 2 else 'media'
                }
            )

# Funciones utilitarias para reglas de negocio

def ejecutar_validaciones_diarias():
    """
    Ejecuta validaciones diarias automáticas
    """
    # Verificar vacunas pendientes
    GestorVacunacion.verificar_vacunas_pendientes()
    
    # Verificar stocks bajos
    from .models import TipoConcentrado
    for tipo in TipoConcentrado.objects.all():
        GestorConcentrado._verificar_stock_bajo(tipo)
    
    # Verificar huevos próximos a vencer
    fecha_limite = timezone.now().date() + timedelta(days=3)
    huevos_por_vencer = MovimientoHuevos.objects.filter(
        tipo_movimiento='entrada',
        cantidad_disponible__gt=0,
        fecha__lte=timezone.now().date() - timedelta(days=18)  # Más de 18 días
    )
    
    for huevo in huevos_por_vencer:
        dias_almacenamiento = (timezone.now().date() - huevo.fecha).days
        AlertaSistema.objects.get_or_create(
            tipo='huevos_por_vencer',
            lote=huevo.lote,
            fecha=timezone.now().date(),
            defaults={
                'mensaje': f"Huevos con {dias_almacenamiento} días de almacenamiento en lote {huevo.lote.codigo}",
                'prioridad': 'alta' if dias_almacenamiento > 19 else 'media'
            }
        )

def generar_reporte_inconsistencias():
    """
    Genera un reporte de inconsistencias en los datos
    """
    from .validators import ValidadorConsistencia
    
    inconsistencias = []
    
    # Verificar lotes activos
    lotes_activos = LoteAves.objects.filter(estado='activo')
    
    for lote in lotes_activos:
        # Verificar últimos 30 días
        fecha_inicio = timezone.now().date() - timedelta(days=30)
        fecha_fin = timezone.now().date()
        
        errores_temporales = ValidadorConsistencia.validar_secuencia_temporal(
            lote, fecha_inicio, fecha_fin
        )
        
        if errores_temporales:
            inconsistencias.extend(errores_temporales)
    
    return inconsistencias