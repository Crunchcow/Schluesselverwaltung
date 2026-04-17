import django.db.models.deletion
from django.db import migrations, models


def delete_assignments_without_person(apps, schema_editor):
    """Remove any assignments that have no person set (test/orphaned data)."""
    KeyAssignment = apps.get_model('keys', 'KeyAssignment')
    KeyAssignment.objects.filter(person__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0002_add_person_model'),
    ]

    operations = [
        # 1. Delete any orphaned assignments so we can make person non-nullable
        migrations.RunPython(
            delete_assignments_without_person,
            reverse_code=migrations.RunPython.noop,
        ),
        # 2. Make person non-nullable and switch to PROTECT
        migrations.AlterField(
            model_name='keyassignment',
            name='person',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assignments',
                to='keys.person',
                verbose_name='Person',
            ),
        ),
        # 3. Drop the redundant free-text fields
        migrations.RemoveField(model_name='keyassignment', name='holder_name'),
        migrations.RemoveField(model_name='keyassignment', name='holder_email'),
        migrations.RemoveField(model_name='keyassignment', name='holder_phone'),
    ]
