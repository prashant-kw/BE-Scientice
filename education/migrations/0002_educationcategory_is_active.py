# Generated manually for EducationCategory.is_active

from django.db import migrations, models


def set_initial_category_active_states(apps, schema_editor):
    EducationCategory = apps.get_model('education', 'EducationCategory')
    # Deactivate CME & Guidelines if present, ensure Patient and Medical are active
    EducationCategory.objects.filter(key='cme').update(is_active=False)
    EducationCategory.objects.exclude(key='cme').update(is_active=True)


def reverse_category_active_states(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcategory',
            name='is_active',
            field=models.BooleanField(
                default=True,
                help_text='Controls whether this education category is enabled and visible on the website'
            ),
        ),
        migrations.RunPython(
            set_initial_category_active_states,
            reverse_category_active_states
        ),
    ]
