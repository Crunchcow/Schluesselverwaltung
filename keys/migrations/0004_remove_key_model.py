import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0003_remove_holder_fields'),
    ]

    operations = [
        # 1. Alle vorhandenen Vergaben löschen (keine Echtdaten auf Server)
        migrations.RunSQL('DELETE FROM keys_keyassignment;', migrations.RunSQL.noop),
        migrations.RunSQL('DELETE FROM keys_key;', migrations.RunSQL.noop),

        # 2. Altes key-FK auf KeyAssignment entfernen
        migrations.RemoveField(model_name='keyassignment', name='key'),

        # 3. Key-Tabelle löschen
        migrations.DeleteModel(name='Key'),

        # 4. total_count auf KeyType
        migrations.AddField(
            model_name='keytype',
            name='total_count',
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name='Gesamtanzahl',
                help_text='Wie viele Schlüssel dieses Typs existieren insgesamt?',
            ),
        ),

        # 5. key_type FK auf KeyAssignment (direkt zu KeyType)
        migrations.AddField(
            model_name='keyassignment',
            name='key_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assignments',
                to='keys.keytype',
                verbose_name='Schlüsseltyp',
                default=1,  # temp default, wird sofort als NOT NULL gesetzt
            ),
            preserve_default=False,
        ),

        # 6. Optionale Schlüsselnummer
        migrations.AddField(
            model_name='keyassignment',
            name='key_number',
            field=models.CharField(
                blank=True, max_length=50,
                verbose_name='Schlüsselnummer',
                help_text='Optional – falls bekannt, z.B. „Nr. 3" oder gravierte Nummer',
            ),
        ),
    ]
