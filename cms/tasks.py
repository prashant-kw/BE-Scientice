import shlex
import subprocess
from pathlib import Path
import requests

from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

from .models import VideoBulletin, VideoGenerationJob


def _update(job, status, progress, error=''):
    job.status = status
    job.progress = progress
    job.error = error
    job.save(update_fields=['status', 'progress', 'error', 'updated_at'])


def _run_template(template, **values):
    if not template:
        raise RuntimeError('The required generation command is not configured.')
    command = template.format(**{key: str(value) for key, value in values.items()})
    # Strip quotes on individual arguments for cross-platform subprocess.run execution
    args = [arg.strip('"\'') for arg in shlex.split(command, posix=(settings.OS_NAME != 'nt' if hasattr(settings, 'OS_NAME') else True))]
    subprocess.run(args, check=True, timeout=45 * 60)



def _studio_still(background_path, avatar_path, output_path):
    background = Image.open(background_path).convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
    avatar = Image.open(avatar_path).convert('RGBA')

    # Advanced background removal (rembg or flood-fill alpha matting)
    try:
        from rembg import remove
        avatar = remove(avatar)
    except Exception:
        # Fallback to high-precision flood-fill alpha matting
        import numpy as np
        from collections import deque

        arr = np.array(avatar)
        h, w, c = arr.shape
        visited = np.zeros((h, w), dtype=bool)
        queue = deque()

        # Seed outer boundary pixels (top row, left/right edges)
        for x in range(w):
            queue.append((0, x))
            visited[0, x] = True
        for y in range(h):
            queue.append((y, 0))
            visited[y, 0] = True
            queue.append((y, w - 1))
            visited[y, w - 1] = True

        # High-precision color matting for white/off-white studio presenter backgrounds
        for y in range(h):
            for x in range(w):
                r, g, b = arr[y, x][:3]
                # Strip pure white & light studio backgrounds (R > 200, G > 200, B > 200)
                if r > 200 and g > 200 and b > 200:
                    arr[y, x, 3] = 0
                elif r > 175 and g > 175 and b > 175 and abs(int(r) - int(g)) < 18 and abs(int(g) - int(b)) < 18:
                    arr[y, x, 3] = 0

        avatar = Image.fromarray(arr)


    avatar.thumbnail((550, 680), Image.Resampling.LANCZOS)
    background.paste(avatar, (55, 720 - avatar.height), avatar)
    background.save(output_path, quality=95)





def _lower_third(title, output_path, bullet_points=None):
    from PIL import Image, ImageDraw, ImageFont

    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. TOP-LEFT LIVE Indicator (Red Badge + Glow)
    draw.rectangle([30, 24, 125, 56], fill=(227, 30, 36, 255))
    draw.ellipse([42, 36, 50, 44], fill=(255, 255, 255, 255))

    # 2. BOTTOM News Ticker Bar Background (Dark Navy) matching web ticker
    draw.rectangle([0, 676, 1280, 720], fill=(7, 19, 40, 255))

    # 3. BOTTOM BREAKING Badge (Bright Red)
    draw.rectangle([0, 676, 145, 720], fill=(217, 4, 41, 255))

    # Fonts
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 13)
        font_live = ImageFont.truetype("arialbd.ttf", 12)
    except Exception:
        font_bold = ImageFont.load_default()
        font_live = font_bold

    # Draw TOP-LEFT LIVE text
    draw.text((58, 32), "LIVE", fill=(255, 255, 255), font=font_live)

    # Draw BOTTOM BREAKING text
    draw.text((18, 691), "● BREAKING", fill=(255, 255, 255), font=font_bold)


    overlay.save(output_path)




import time
import wave
import contextlib


def _get_audio_duration(wav_path):
    try:
        with contextlib.closing(wave.open(str(wav_path), 'rb')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)
    except Exception:
        return 0.0

def _split_wav(input_wav_path, chunks_dir, max_chunk_seconds=300):
    """Splits a WAV audio file into chunks of max_chunk_seconds."""
    chunks_dir.mkdir(parents=True, exist_ok=True)
    with wave.open(str(input_wav_path), 'rb') as wav_in:
        params = wav_in.getparams()
        framerate = wav_in.getframerate()
        frames_per_chunk = int(framerate * max_chunk_seconds)
        total_frames = wav_in.getnframes()

        chunk_files = []
        chunk_idx = 0
        while wav_in.tell() < total_frames:
            chunk_frames = wav_in.readframes(frames_per_chunk)
            if not chunk_frames:
                break
            chunk_path = chunks_dir / f'chunk_{chunk_idx:02d}.wav'
            with wave.open(str(chunk_path), 'wb') as wav_out:
                wav_out.setparams(params)
                wav_out.writeframes(chunk_frames)
            chunk_files.append(chunk_path)
            chunk_idx += 1
        return chunk_files

def _animate_avatar_replicate_with_retry(
    image_path,
    audio_path,
    output_mp4_path,
    api_token,
    generation_retries=1,
    download_retries=3,
):
    """
    Generate an avatar video with Replicate and download it safely.

    Paid generation retries and download retries are intentionally separated.
    Once Replicate returns a result URL, download failures must never trigger
    another paid generation request.
    """
    import replicate

    output_mp4_path = Path(output_mp4_path)

    # Reuse a completed local artifact from a previous attempt of the same job.
    if output_mp4_path.exists() and output_mp4_path.stat().st_size > 0:
        return

    client = replicate.Client(api_token=api_token)
    video_url = None
    generation_error = None

    # Persist the generated URL next to the target MP4. If generation succeeds
    # but downloading fails, rerunning the SAME job resumes the download instead
    # of creating another paid Replicate prediction.
    url_cache_path = output_mp4_path.with_suffix(output_mp4_path.suffix + '.url')
    if url_cache_path.exists():
        cached_url = url_cache_path.read_text(encoding='utf-8').strip()
        if cached_url:
            video_url = cached_url

    # STEP 1: paid Replicate generation. Only run when neither the final local
    # MP4 nor a previously returned Replicate URL is available.
    if not video_url:
        for attempt in range(1, generation_retries + 1):
            try:
                with open(image_path, 'rb') as img_f, open(audio_path, 'rb') as aud_f:
                    # Upload source files first to obtain remote URLs
                    img_file = client.files.create(img_f)
                    aud_file = client.files.create(aud_f)

                    # Create async prediction & poll up to 10 minutes (prevents HTTP socket timeout)
                    prediction = client.predictions.create(
                        version="cjwbw/sadtalker:a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3",
                        input={
                            "source_image": img_file.urls["get"],
                            "driven_audio": aud_file.urls["get"],
                            "still": True,
                            "preprocess": "full",
                            "enhancer": "gfpgan",
                        },
                    )

                    # Poll prediction until completion
                    prediction.wait()

                    if prediction.status != "succeeded":
                        raise RuntimeError(f"Replicate prediction failed with status '{prediction.status}': {prediction.error}")

                    output = prediction.output

                video_url = str(output).strip()
                if not video_url:
                    raise RuntimeError('Replicate completed but returned no video URL.')

                # Save immediately, before attempting the download.
                url_cache_path.write_text(video_url, encoding='utf-8')
                break
            except Exception as err:
                generation_error = err
                if attempt < generation_retries:
                    time.sleep(4 * attempt)


        if not video_url:
            raise RuntimeError(
                f'Replicate generation failed after {generation_retries} attempt(s): {generation_error}'
            )

    # STEP 2: download the already-generated asset. Retrying this is safe and
    # does not create another Replicate generation request.
    temp_path = output_mp4_path.with_suffix(output_mp4_path.suffix + '.part')
    download_error = None

    for attempt in range(1, download_retries + 1):
        try:
            with requests.get(video_url, timeout=300, stream=True) as resp:
                resp.raise_for_status()
                with open(temp_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)

            if not temp_path.exists() or temp_path.stat().st_size == 0:
                raise RuntimeError('Downloaded Replicate video is empty.')

            temp_path.replace(output_mp4_path)
            return
        except Exception as err:
            download_error = err
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            if attempt < download_retries:
                time.sleep(4 * attempt)

    raise RuntimeError(
        'Replicate generation succeeded, but downloading the generated video '
        f'failed after {download_retries} attempts: {download_error}'
    )



@shared_task(bind=True)
def generate_video_bulletin(self, job_id):
    job = VideoGenerationJob.objects.select_related('bulletin').get(pk=job_id)
    bulletin = job.bulletin
    job.task_id = self.request.id or ''
    job.started_at = timezone.now()
    job.save(update_fields=['task_id', 'started_at', 'updated_at'])

    root = Path(settings.VIDEO_GENERATION_ROOT) / f'job-{job.id}'
    root.mkdir(parents=True, exist_ok=True)
    chunks_dir = root / 'chunks'
    script_file = root / 'script.txt'
    audio_file = root / 'narration.wav'
    studio_still = root / 'studio-still.jpg'
    avatar_output = root / 'avatar-output'
    final_file = root / 'final-bulletin.mp4'
    overlay_file = root / 'lower-third.png'

    try:
        media_root = Path(settings.MEDIA_ROOT)
        bg_path = Path(bulletin.background_image.path) if bulletin.background_image else media_root / 'video_bulletins' / 'backgrounds' / 'prototype-newsroom.png'
        avatar_path = Path(bulletin.custom_avatar_image.path) if bulletin.custom_avatar_image else media_root / 'video_bulletins' / 'avatars' / 'prototype-anchor.png'

        if not bg_path.exists() or not avatar_path.exists():
            raise RuntimeError('Both an avatar presenter image and a background image are required.')
        script_file.write_text(bulletin.script or 'Welcome to the Global Cardiology Bulletin.', encoding='utf-8')

        _update(job, VideoGenerationJob.Status.AUDIO, 15)
        voice_gender = getattr(bulletin, 'voice_gender', 'female') or 'female'
        _run_template(settings.VIDEO_TTS_COMMAND, script_file=script_file, audio_file=audio_file,
                      avatar_file=str(avatar_path), output_dir=avatar_output, voice_gender=voice_gender)



        _studio_still(bg_path, avatar_path, studio_still)
        avatar_output.mkdir(exist_ok=True)

        _update(job, VideoGenerationJob.Status.AVATAR, 45)

        replicate_token = getattr(settings, 'REPLICATE_API_TOKEN', '')
        if replicate_token:
            # Check audio duration
            duration_sec = _get_audio_duration(audio_file)
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

            # Split audio if longer than 5 minutes (300 seconds)
            if duration_sec > 300:
                audio_chunks = _split_wav(audio_file, chunks_dir, max_chunk_seconds=300)
                total_chunks = len(audio_chunks)
                rendered_mp4s = []

                for idx, chunk_wav in enumerate(audio_chunks, start=1):
                    chunk_mp4 = chunks_dir / f'rendered_{idx:02d}.mp4'
                    chunk_pct = 45 + int((idx / total_chunks) * 30)
                    _update(job, VideoGenerationJob.Status.AVATAR, chunk_pct, f'Processing chunk {idx} of {total_chunks} via Replicate API…')

                    # Check disk cache: if already rendered in a previous partial run, reuse it!
                    if not chunk_mp4.exists() or chunk_mp4.stat().st_size == 0:
                        _animate_avatar_replicate_with_retry(studio_still, chunk_wav, chunk_mp4, replicate_token)
                    rendered_mp4s.append(chunk_mp4)

                _update(job, VideoGenerationJob.Status.COMPOSING, 76, f'Stitching {total_chunks} generated video chunks via FFmpeg…')
                # Concatenate rendered MP4 chunks using FFmpeg
                concat_list_file = root / 'concat_list.txt'
                with open(concat_list_file, 'w', encoding='utf-8') as f:
                    for mp4 in rendered_mp4s:
                        f.write(f"file '{mp4.resolve()}'\n")

                stitched_avatar_mp4 = root / 'replicate-stitched.mp4'
                subprocess.run([
                    ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_list_file),
                    '-c', 'copy', str(stitched_avatar_mp4)
                ], check=True, timeout=10 * 60)
                source_avatar_mp4 = stitched_avatar_mp4
            else:
                replicate_mp4 = root / 'replicate-avatar.mp4'
                if not replicate_mp4.exists() or replicate_mp4.stat().st_size == 0:
                    _animate_avatar_replicate_with_retry(studio_still, audio_file, replicate_mp4, replicate_token)
                source_avatar_mp4 = replicate_mp4


        elif settings.VIDEO_SADTALKER_COMMAND:
            _run_template(settings.VIDEO_SADTALKER_COMMAND, script_file=script_file, audio_file=audio_file,
                          avatar_file=studio_still, output_dir=avatar_output)
            candidates = sorted(avatar_output.rglob('*.mp4'), key=lambda item: item.stat().st_mtime, reverse=True)
            if not candidates:
                raise RuntimeError('SadTalker completed without producing an MP4.')
            source_avatar_mp4 = candidates[0]
        else:
            raise RuntimeError('Neither REPLICATE_API_TOKEN nor VIDEO_SADTALKER_COMMAND is configured.')

        _update(job, VideoGenerationJob.Status.COMPOSING, 78)
        b_points = bulletin.bullet_points if isinstance(bulletin.bullet_points, list) else []
        _lower_third(bulletin.title, overlay_file, bullet_points=b_points)
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

        try:
            subprocess.run(
                [
                    ffmpeg, '-y',
                    '-i', str(source_avatar_mp4),
                    '-i', str(overlay_file),
                    '-filter_complex', '[0:v]scale=1280:720[base];[base][1:v]overlay=0:0:format=auto',
                    '-map', '0:a?',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '20',
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac',
                    '-b:a', '160k',
                    '-movflags', '+faststart',
                    str(final_file),
                ],
                check=True,
                timeout=20 * 60,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            ffmpeg_error = exc.stderr or exc.stdout or str(exc)
            raise RuntimeError(
                f"FFmpeg final composition failed:\n{ffmpeg_error[-3500:]}"
            ) from exc



        with final_file.open('rb') as generated:
            bulletin.video_file.save(f'{bulletin.slug}-{job.id}.mp4', File(generated), save=False)
        duration_sec = _get_audio_duration(audio_file)
        if duration_sec > 0:
            bulletin.duration_seconds = int(round(duration_sec))
        bulletin.save(update_fields=['video_file', 'duration_seconds', 'updated_at'])

        job.output_file.name = bulletin.video_file.name

        job.status = VideoGenerationJob.Status.READY
        job.progress = 100
        job.completed_at = timezone.now()
        job.save(update_fields=['output_file', 'status', 'progress', 'completed_at', 'updated_at'])
    except Exception as exc:
        job.completed_at = timezone.now()
        job.save(update_fields=['completed_at', 'updated_at'])
        _update(job, VideoGenerationJob.Status.FAILED, job.progress, str(exc)[:4000])
        raise


