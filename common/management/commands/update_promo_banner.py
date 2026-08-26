import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from cms.models import VideoBulletin

class Command(BaseCommand):
    help = 'Update VideoBulletin promo banner image to the new ESC Congress 2026 design'

    def handle(self, *args, **options):
        # 1. Source image from user upload directory
        source_paths = [
            Path(r"C:\Users\Prashant\.gemini\antigravity-ide\brain\cae9b5c4-ee69-4d7c-bd43-34216e33476e\.user_uploaded\media_1787742908615.jpg"),
        ]

        source_file = None
        for p in source_paths:
            if p.exists():
                source_file = p
                break

        if not source_file:
            self.stdout.write(self.style.ERROR(f'Source image not found in: {source_paths[0]}'))
            return

        self.stdout.write(f'Found source image at: {source_file}')

        # 2. Target destinations
        base_dir = Path(settings.BASE_DIR)
        media_root = Path(settings.MEDIA_ROOT)
        fe_public = base_dir.parent / 'frontend' / 'FE-Scientice' / 'public'
        fe_assets = base_dir.parent / 'frontend' / 'FE-Scientice' / 'src' / 'assets'
        banners_dir = media_root / 'video_bulletins' / 'banners'
        backgrounds_dir = media_root / 'video_bulletins' / 'backgrounds'

        banners_dir.mkdir(parents=True, exist_ok=True)
        backgrounds_dir.mkdir(parents=True, exist_ok=True)
        fe_public.mkdir(parents=True, exist_ok=True)
        fe_assets.mkdir(parents=True, exist_ok=True)

        target_banner = banners_dir / 'esc-congress-2026-promo.jpg'
        target_bg = backgrounds_dir / 'esc-congress-2026-promo.jpg'
        target_fe_public = fe_public / 'esc-congress-2026-promo.jpg'
        target_fe_assets = fe_assets / 'esc-congress-2026-promo.jpg'

        shutil.copy2(source_file, target_banner)
        shutil.copy2(source_file, target_bg)
        shutil.copy2(source_file, target_fe_public)
        shutil.copy2(source_file, target_fe_assets)

        self.stdout.write(self.style.SUCCESS(f'Copied banner image to: {target_banner}'))
        self.stdout.write(self.style.SUCCESS(f'Copied background image to: {target_bg}'))
        self.stdout.write(self.style.SUCCESS(f'Copied frontend public asset to: {target_fe_public}'))

        # 3. Update VideoBulletin records in Database
        bulletins = VideoBulletin.objects.all()
        if not bulletins.exists():
            self.stdout.write(self.style.WARNING('No VideoBulletin records found to update.'))
            return

        updated_count = 0
        for b in bulletins:
            b.promo_banner_image = 'video_bulletins/banners/esc-congress-2026-promo.jpg'
            b.background_image = 'video_bulletins/backgrounds/esc-congress-2026-promo.jpg'
            b.background_image_url = ''
            if not b.event_title or 'ESC' in b.event_title or 'Congress' in b.event_title:
                b.event_title = 'ESC Congress 2026'
            b.save()
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'Updated bulletin ID {b.id} ({b.title}): promo_banner_image set to esc-congress-2026-promo.jpg'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} VideoBulletin record(s)!'))
