"""
Pruebas integrales para el módulo avícola
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    LoteAves, BitacoraProduccion, MovimientoHuevos, 
    InventarioHuevos, PlanVacunacion, AlertaAvicola
)
from .forms import LoteAvesForm, BitacoraProduccionForm
from .business_rules import GestorLoteAves, GestorProduccion, GestorMovimientoHuevos
from .validators import ValidadorAvicola, ValidadorConsistencia

User = get_user_model()

class LoteAvesModelTest(TestCase):
    """Pruebas para el modelo LoteAves"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_crear_lote_aves(self):
        """Prueba la creación de un lote de aves"""
        lote = LoteAves.objects.create(
            codigo='L001',
            raza='Rhode Island Red',
            cantidad_inicial=1000,
            fecha_ingreso=date.today(),
            galpon_id=1,
            creado_por=self.user
        )
        
        self.assertEqual(lote.codigo, 'L001')
        self.assertEqual(lote.cantidad_actual, 1000)
        self.assertEqual(lote.estado, 'activo')
        self.assertIsNotNone(lote.fecha_creacion)
        
    def test_calcular_edad_lote(self):
        """Prueba el cálculo de edad del lote"""
        fecha_ingreso = date.today() - timedelta(days=30)
        lote = LoteAves.objects.create(
            codigo='L002',
            raza='Leghorn',
            cantidad_inicial=500,
            fecha_ingreso=fecha_ingreso,
            galpon_id=1,
            creado_por=self.user
        )
        
        self.assertEqual(lote.edad_dias, 30)
        
    def test_lote_str_representation(self):
        """Prueba la representación string del lote"""
        lote = LoteAves.objects.create(
            codigo='L003',
            raza='Plymouth Rock',
            cantidad_inicial=800,
            fecha_ingreso=date.today(),
            galpon_id=1,
            creado_por=self.user
        )
        
        expected = f"L003 - Plymouth Rock (800 aves)"
        self.assertEqual(str(lote), expected)

class BitacoraProduccionModelTest(TestCase):
    """Pruebas para el modelo BitacoraProduccion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.lote = LoteAves.objects.create(
            codigo='L001',
            raza='Rhode Island Red',
            cantidad_inicial=1000,
            fecha_ingreso=date.today() - timedelta(days=120),
            galpon_id=1,
            creado_por=self.user
        )
        
    def test_crear_bitacora_produccion(self):
        """Prueba la creación de una bitácora de producción"""
        bitacora = BitacoraProduccion.objects.create(
            lote=self.lote,
            fecha=date.today(),
            huevos_producidos=850,
            mortalidad=2,
            consumo_concentrado=Decimal('120.5'),
            temperatura_promedio=Decimal('22.5'),
            humedad_promedio=Decimal('65.0'),
            registrado_por=self.user
        )
        
        self.assertEqual(bitacora.huevos_producidos, 850)
        self.assertEqual(bitacora.mortalidad, 2)
        self.assertEqual(bitacora.consumo_concentrado, Decimal('120.5'))
        
    def test_calcular_porcentaje_postura(self):
        """Prueba el cálculo del porcentaje de postura"""
        bitacora = BitacoraProduccion.objects.create(
            lote=self.lote,
            fecha=date.today(),
            huevos_producidos=800,
            mortalidad=0,
            consumo_concentrado=Decimal('120.0'),
            registrado_por=self.user
        )
        
        # 800 huevos / 1000 aves = 80%
        self.assertEqual(bitacora.porcentaje_postura, 80.0)

class ValidadorAvicolaTest(TestCase):
    """Pruebas para el validador avícola"""
    
    def setUp(self):
        self.validador = ValidadorAvicola()
        
    def test_validar_fecha_valida(self):
        """Prueba validación de fecha válida"""
        fecha_valida = date.today()
        resultado = self.validador.validar_fecha(fecha_valida)
        self.assertTrue(resultado['valido'])
        
    def test_validar_fecha_futura(self):
        """Prueba validación de fecha futura"""
        fecha_futura = date.today() + timedelta(days=1)
        resultado = self.validador.validar_fecha(fecha_futura)
        self.assertFalse(resultado['valido'])
        self.assertIn('futuro', resultado['mensaje'])
        
    def test_validar_produccion_huevos_valida(self):
        """Prueba validación de producción de huevos válida"""
        resultado = self.validador.validar_produccion_huevos(800, 1000)
        self.assertTrue(resultado['valido'])
        
    def test_validar_produccion_huevos_excesiva(self):
        """Prueba validación de producción excesiva"""
        resultado = self.validador.validar_produccion_huevos(1200, 1000)
        self.assertFalse(resultado['valido'])
        self.assertIn('excede', resultado['mensaje'])
        
    def test_validar_mortalidad_normal(self):
        """Prueba validación de mortalidad normal"""
        resultado = self.validador.validar_mortalidad(5, 1000)
        self.assertTrue(resultado['valido'])
        
    def test_validar_mortalidad_alta(self):
        """Prueba validación de mortalidad alta"""
        resultado = self.validador.validar_mortalidad(60, 1000)  # 6%
        self.assertFalse(resultado['valido'])
        self.assertIn('alta', resultado['mensaje'])

class GestorLoteAvesTest(TestCase):
    """Pruebas para el gestor de lotes de aves"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.gestor = GestorLoteAves()
        
    def test_crear_lote_exitoso(self):
        """Prueba la creación exitosa de un lote"""
        datos = {
            'codigo': 'L001',
            'raza': 'Rhode Island Red',
            'cantidad_inicial': 1000,
            'fecha_ingreso': date.today(),
            'galpon_id': 1
        }
        
        resultado = self.gestor.crear_lote(datos, self.user)
        self.assertTrue(resultado['exito'])
        self.assertIsNotNone(resultado['lote'])
        
    def test_crear_lote_codigo_duplicado(self):
        """Prueba la creación de lote con código duplicado"""
        # Crear primer lote
        LoteAves.objects.create(
            codigo='L001',
            raza='Rhode Island Red',
            cantidad_inicial=1000,
            fecha_ingreso=date.today(),
            galpon_id=1,
            creado_por=self.user
        )
        
        # Intentar crear segundo lote con mismo código
        datos = {
            'codigo': 'L001',
            'raza': 'Leghorn',
            'cantidad_inicial': 500,
            'fecha_ingreso': date.today(),
            'galpon_id': 2
        }
        
        resultado = self.gestor.crear_lote(datos, self.user)
        self.assertFalse(resultado['exito'])
        self.assertIn('código ya existe', resultado['mensaje'])

class GestorProduccionTest(TestCase):
    """Pruebas para el gestor de producción"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.lote = LoteAves.objects.create(
            codigo='L001',
            raza='Rhode Island Red',
            cantidad_inicial=1000,
            fecha_ingreso=date.today() - timedelta(days=120),
            galpon_id=1,
            creado_por=self.user
        )
        
        self.gestor = GestorProduccion()
        
    def test_registrar_produccion_exitosa(self):
        """Prueba el registro exitoso de producción"""
        datos = {
            'lote': self.lote,
            'fecha': date.today(),
            'huevos_producidos': 800,
            'mortalidad': 2,
            'consumo_concentrado': Decimal('120.0'),
            'temperatura_promedio': Decimal('22.5'),
            'humedad_promedio': Decimal('65.0')
        }
        
        resultado = self.gestor.registrar_produccion_diaria(datos, self.user)
        self.assertTrue(resultado['exito'])
        self.assertIsNotNone(resultado['bitacora'])
        
    def test_registrar_produccion_duplicada(self):
        """Prueba el registro de producción duplicada"""
        # Crear primera bitácora
        BitacoraProduccion.objects.create(
            lote=self.lote,
            fecha=date.today(),
            huevos_producidos=800,
            mortalidad=2,
            consumo_concentrado=Decimal('120.0'),
            registrado_por=self.user
        )
        
        # Intentar crear segunda bitácora para la misma fecha
        datos = {
            'lote': self.lote,
            'fecha': date.today(),
            'huevos_producidos': 850,
            'mortalidad': 1,
            'consumo_concentrado': Decimal('125.0')
        }
        
        resultado = self.gestor.registrar_produccion_diaria(datos, self.user)
        self.assertFalse(resultado['exito'])
        self.assertIn('ya existe', resultado['mensaje'])

class MovimientoHuevosTest(TestCase):
    """Pruebas para movimientos de huevos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.lote = LoteAves.objects.create(
            codigo='L001',
            raza='Rhode Island Red',
            cantidad_inicial=1000,
            fecha_ingreso=date.today() - timedelta(days=120),
            galpon_id=1,
            creado_por=self.user
        )
        
        # Crear inventario inicial
        self.inventario = InventarioHuevos.objects.create(
            lote=self.lote,
            fecha_produccion=date.today(),
            cantidad_inicial=800,
            cantidad_actual=800,
            peso_promedio=Decimal('60.5')
        )
        
    def test_crear_movimiento_salida(self):
        """Prueba la creación de movimiento de salida"""
        movimiento = MovimientoHuevos.objects.create(
            inventario=self.inventario,
            tipo_movimiento='salida',
            cantidad=100,
            destino='Cliente A',
            fecha_movimiento=timezone.now(),
            registrado_por=self.user
        )
        
        self.assertEqual(movimiento.cantidad, 100)
        self.assertEqual(movimiento.tipo_movimiento, 'salida')
        
        # Verificar que se actualizó el inventario
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_actual, 700)

class ViewsTest(TestCase):
    """Pruebas para las vistas del módulo"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_dashboard_view(self):
        """Prueba la vista del dashboard"""
        response = self.client.get(reverse('aves:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Avícola')
        
    def test_crear_lote_view_get(self):
        """Prueba la vista GET para crear lote"""
        response = self.client.get(reverse('aves:crear_lote'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
    def test_crear_lote_view_post(self):
        """Prueba la vista POST para crear lote"""
        data = {
            'codigo': 'L001',
            'raza': 'Rhode Island Red',
            'cantidad_inicial': 1000,
            'fecha_ingreso': date.today(),
            'galpon': 1,
            'observaciones': 'Lote de prueba'
        }
        
        response = self.client.post(reverse('aves:crear_lote'), data)
        self.assertEqual(response.status_code, 302)  # Redirect después de crear
        
        # Verificar que se creó el lote
        lote = LoteAves.objects.get(codigo='L001')
        self.assertEqual(lote.raza, 'Rhode Island Red')

class FormsTest(TestCase):
    """Pruebas para los formularios"""
    
    def test_lote_aves_form_valido(self):
        """Prueba formulario válido de lote de aves"""
        form_data = {
            'codigo': 'L001',
            'raza': 'Rhode Island Red',
            'cantidad_inicial': 1000,
            'fecha_ingreso': date.today(),
            'galpon': 1,
            'observaciones': 'Lote de prueba'
        }
        
        form = LoteAvesForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_lote_aves_form_codigo_vacio(self):
        """Prueba formulario con código vacío"""
        form_data = {
            'codigo': '',
            'raza': 'Rhode Island Red',
            'cantidad_inicial': 1000,
            'fecha_ingreso': date.today(),
            'galpon': 1
        }
        
        form = LoteAvesForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)
        
    def test_bitacora_produccion_form_valido(self):
        """Prueba formulario válido de bitácora de producción"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        lote = LoteAves.objects.create(
            codigo='L001',
            raza='Rhode Island Red',
            cantidad_inicial=1000,
            fecha_ingreso=date.today() - timedelta(days=120),
            galpon_id=1,
            creado_por=user
        )
        
        form_data = {
            'lote': lote.id,
            'fecha': date.today(),
            'huevos_producidos': 800,
            'mortalidad': 2,
            'consumo_concentrado': '120.5',
            'temperatura_promedio': '22.5',
            'humedad_promedio': '65.0'
        }
        
        form = BitacoraProduccionForm(data=form_data)
        self.assertTrue(form.is_valid())

class IntegrationTest(TestCase):
    """Pruebas de integración completas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_flujo_completo_produccion(self):
        """Prueba el flujo completo desde crear lote hasta registrar producción"""
        # 1. Crear lote
        gestor_lote = GestorLoteAves()
        datos_lote = {
            'codigo': 'L001',
            'raza': 'Rhode Island Red',
            'cantidad_inicial': 1000,
            'fecha_ingreso': date.today() - timedelta(days=120),
            'galpon_id': 1
        }
        
        resultado_lote = gestor_lote.crear_lote(datos_lote, self.user)
        self.assertTrue(resultado_lote['exito'])
        lote = resultado_lote['lote']
        
        # 2. Registrar producción
        gestor_produccion = GestorProduccion()
        datos_produccion = {
            'lote': lote,
            'fecha': date.today(),
            'huevos_producidos': 800,
            'mortalidad': 2,
            'consumo_concentrado': Decimal('120.0'),
            'temperatura_promedio': Decimal('22.5'),
            'humedad_promedio': Decimal('65.0')
        }
        
        resultado_produccion = gestor_produccion.registrar_produccion_diaria(
            datos_produccion, self.user
        )
        self.assertTrue(resultado_produccion['exito'])
        
        # 3. Verificar que se creó el inventario de huevos
        inventario = InventarioHuevos.objects.filter(lote=lote).first()
        self.assertIsNotNone(inventario)
        self.assertEqual(inventario.cantidad_inicial, 800)
        
        # 4. Crear movimiento de huevos
        gestor_movimiento = GestorMovimientoHuevos()
        datos_movimiento = {
            'inventario': inventario,
            'tipo_movimiento': 'salida',
            'cantidad': 100,
            'destino': 'Cliente A'
        }
        
        resultado_movimiento = gestor_movimiento.despachar_huevos(
            datos_movimiento, self.user
        )
        self.assertTrue(resultado_movimiento['exito'])
        
        # 5. Verificar actualización de inventario
        inventario.refresh_from_db()
        self.assertEqual(inventario.cantidad_actual, 700)
        
        # 6. Verificar actualización de cantidad de aves
        lote.refresh_from_db()
        self.assertEqual(lote.cantidad_actual, 998)  # 1000 - 2 mortalidad

class PerformanceTest(TestCase):
    """Pruebas de rendimiento"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_consulta_dashboard_performance(self):
        """Prueba el rendimiento de la consulta del dashboard"""
        # Crear datos de prueba
        for i in range(10):
            lote = LoteAves.objects.create(
                codigo=f'L{i:03d}',
                raza='Rhode Island Red',
                cantidad_inicial=1000,
                fecha_ingreso=date.today() - timedelta(days=120),
                galpon_id=i + 1,
                creado_por=self.user
            )
            
            # Crear bitácoras para cada lote
            for j in range(30):  # 30 días de producción
                BitacoraProduccion.objects.create(
                    lote=lote,
                    fecha=date.today() - timedelta(days=j),
                    huevos_producidos=800 + j,
                    mortalidad=j % 3,
                    consumo_concentrado=Decimal('120.0'),
                    registrado_por=self.user
                )
        
        # Medir tiempo de consulta
        import time
        start_time = time.time()
        
        # Simular consultas del dashboard
        lotes_activos = LoteAves.objects.filter(estado='activo').count()
        produccion_total = BitacoraProduccion.objects.filter(
            fecha__gte=date.today() - timedelta(days=7)
        ).count()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Verificar que las consultas son rápidas (menos de 1 segundo)
        self.assertLess(query_time, 1.0)
        self.assertGreater(lotes_activos, 0)
        self.assertGreater(produccion_total, 0)