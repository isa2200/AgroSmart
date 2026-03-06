from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('aves', '0004_alter_alertasistema_nivel'),
    ]

    operations = [
        migrations.AddField(
            model_name='loteaves',
            name='tipo',
            field=models.CharField(default='ponedoras', max_length=20),
        ),
    ]
