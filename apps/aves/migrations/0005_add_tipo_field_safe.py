# Generated manually to handle duplicate column issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aves', '0004_alter_alertasistema_nivel'),
    ]

    operations = [
        migrations.RunSQL(
            # Verificar si la columna existe antes de agregarla
            sql="""
            SET @col_exists = 0;
            SELECT COUNT(*) INTO @col_exists 
            FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'aves_loteaves' 
            AND column_name = 'tipo';
            
            SET @sql = IF(@col_exists = 0, 
                'ALTER TABLE aves_loteaves ADD COLUMN tipo VARCHAR(20) NOT NULL DEFAULT "ponedoras"',
                'SELECT "Column tipo already exists" as message'
            );
            
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
            """,
            reverse_sql="""
            ALTER TABLE aves_loteaves DROP COLUMN IF EXISTS tipo;
            """
        ),
    ]