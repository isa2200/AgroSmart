from django.db import migrations


def seed_tipo_vacuna(apps, schema_editor):
    TipoVacuna = apps.get_model('aves', 'TipoVacuna')
    defaults = [
        {
            'nombre': 'Marek (HVT)',
            'laboratorio': 'Genérico',
            'enfermedad_previene': 'Enfermedad de Marek',
            'via_aplicacion': 'Subcutánea (día 1)',
            'dosis_por_ave': 0.2,
            'intervalo_dias': None,
        },
        {
            'nombre': 'Newcastle (LaSota)',
            'laboratorio': 'Genérico',
            'enfermedad_previene': 'Newcastle',
            'via_aplicacion': 'Agua de bebida / Spray / Ocular',
            'dosis_por_ave': 0.03,
            'intervalo_dias': 21,
        },
        {
            'nombre': 'Gumboro (IBD)',
            'laboratorio': 'Genérico',
            'enfermedad_previene': 'Enfermedad de Gumboro (IBD)',
            'via_aplicacion': 'Agua de bebida',
            'dosis_por_ave': 0.03,
            'intervalo_dias': 14,
        },
        {
            'nombre': 'Bronquitis Infecciosa (Mass.)',
            'laboratorio': 'Genérico',
            'enfermedad_previene': 'Bronquitis infecciosa',
            'via_aplicacion': 'Ocular / Spray',
            'dosis_por_ave': 0.03,
            'intervalo_dias': 21,
        },
        {
            'nombre': 'Viruela Aviar (Pox)',
            'laboratorio': 'Genérico',
            'enfermedad_previene': 'Viruela aviar',
            'via_aplicacion': 'Membrana del ala (wing-web)',
            'dosis_por_ave': 0.1,
            'intervalo_dias': None,
        },
        {
            'nombre': 'Coccidiosis (viva atenuada)',
            'laboratorio': 'Genérico',
            'enfermedad_previene': 'Coccidiosis',
            'via_aplicacion': 'Spray / Agua de bebida',
            'dosis_por_ave': 0.1,
            'intervalo_dias': None,
        },
    ]

    existing_names = set(TipoVacuna.objects.values_list('nombre', flat=True))
    to_create = [TipoVacuna(**d) for d in defaults if d['nombre'] not in existing_names]
    if to_create:
        TipoVacuna.objects.bulk_create(to_create)


def unseed_tipo_vacuna(apps, schema_editor):
    TipoVacuna = apps.get_model('aves', 'TipoVacuna')
    names = [
        'Marek (HVT)',
        'Newcastle (LaSota)',
        'Gumboro (IBD)',
        'Bronquitis Infecciosa (Mass.)',
        'Viruela Aviar (Pox)',
        'Coccidiosis (viva atenuada)',
    ]
    TipoVacuna.objects.filter(nombre__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aves', '0011_inventarioaves'),
    ]

    operations = [
        migrations.RunPython(seed_tipo_vacuna, reverse_code=unseed_tipo_vacuna),
    ]

