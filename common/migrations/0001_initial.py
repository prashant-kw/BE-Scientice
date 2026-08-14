import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actor_email', models.EmailField(blank=True, default='', help_text='Email address used during the auth event', max_length=254, verbose_name='attempted / authenticated email')),
                ('action', models.CharField(choices=[('LOGIN_SUCCESS', 'Login Success'), ('LOGIN_FAILED', 'Login Failed'), ('USER_REGISTERED', 'User Registered'), ('LOGOUT', 'Logout'), ('PASSWORD_CHANGED', 'Password Changed')], db_index=True, max_length=50)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')),
                ('user_agent', models.TextField(blank=True, default='', verbose_name='User Agent')),
                ('details', models.JSONField(blank=True, default=dict, verbose_name='Context Details')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(blank=True, help_text='Associated user account if resolved', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auth_audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Authentication Audit Log',
                'verbose_name_plural': 'Authentication Audit Logs',
                'ordering': ['-timestamp'],
            },
        ),
    ]
