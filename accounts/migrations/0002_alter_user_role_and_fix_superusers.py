from django.db import migrations, models

def fix_existing_superusers(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    # Update all superusers and specifically the admin account
    User.objects.filter(is_superuser=True).update(is_staff=True, role='admin')
    User.objects.filter(email__iexact='admin@scientice.org').update(
        is_staff=True,
        is_superuser=True,
        role='admin'
    )

def reverse_fix(apps, schema_editor):
    # No-op reverse operation
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Administrator'),
                    ('doctor', 'Physician / Doctor'),
                    ('researcher', 'Researcher / Scientist'),
                    ('pharmacist', 'Pharmacist'),
                    ('student', 'Medical Student'),
                    ('patient', 'Patient / Caregiver'),
                    ('others', 'Others')
                ],
                default='doctor',
                help_text='Professional role or identity badge (Display only; authorization relies on is_staff/is_superuser)',
                max_length=30
            ),
        ),
        migrations.RunPython(fix_existing_superusers, reverse_code=reverse_fix),
    ]
