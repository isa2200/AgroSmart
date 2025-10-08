# Generated migration for stock automático fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aves', '0002_add_detalle_movimiento_huevos'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventariohuevos',
            name='stock_automatico',
            field=models.BooleanField(default=True, help_text='Si está activado, el stock mínimo se calcula automáticamente basado en la cantidad de gallinas', verbose_name='Stock automático'),
        ),
        migrations.AddField(
            model_name='inventariohuevos',
            name='factor_calculo',
            field=models.DecimalField(decimal_places=2, default=0.75, help_text='Factor multiplicador para calcular stock mínimo (ej: 0.75 = 75% de producción esperada)', max_digits=5, verbose_name='Factor de cálculo'),
        ),
        migrations.AddField(
            model_name='inventariohuevos',
            name='dias_stock',
            field=models.PositiveIntegerField(default=3, help_text='Número de días de stock mínimo a mantener', verbose_name='Días de stock'),
        ),
    ]