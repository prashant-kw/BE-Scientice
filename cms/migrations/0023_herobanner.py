# Generated for HeroBanner model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_alter_presenteravatar_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(default='Cardiovascular knowledge,\ndelivered with clinical precision', help_text='Main headline on the hero banner (supports newlines)', max_length=255)),
                ('kicker', models.CharField(blank=True, default='', help_text='Optional small category/kicker above headline', max_length=150)),
                ('banner_image', models.ImageField(blank=True, help_text='Upload custom banner image (JPG, PNG, WebP)', max_length=500, null=True, upload_to='hero_banners/')),
                ('image_alt_text', models.CharField(blank=True, default='Scientice Hero Banner', max_length=200)),
                ('primary_button_text', models.CharField(blank=True, default='Watch latest report', help_text='Text for the main button', max_length=100)),
                ('primary_button_link', models.CharField(blank=True, default='', help_text='Link for main button (e.g. #guidelines-home-section or URL or bulletin slug)', max_length=500)),
                ('secondary_button_text', models.CharField(blank=True, default='', help_text='Optional text for bottom/secondary link button', max_length=100)),
                ('secondary_button_link', models.CharField(blank=True, default='', help_text='URL or anchor for secondary button (e.g. #guidelines-home-section)', max_length=500)),
                ('show_countdown_timer', models.BooleanField(default=False, help_text='Display live reverse countdown on the banner')),
                ('timer_label', models.CharField(blank=True, default='Event Countdown', help_text='Label text next to countdown pulse dot', max_length=150)),
                ('event_start_datetime', models.DateTimeField(blank=True, help_text='Target datetime for countdown timer', null=True)),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Toggle hero banner active status. Highest active banner is shown on homepage.')),
            ],
            options={
                'verbose_name': 'Hero Banner',
                'verbose_name_plural': 'Hero Banners',
                'ordering': ['-is_active', '-updated_at', '-created_at'],
            },
        ),
    ]
