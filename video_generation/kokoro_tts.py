import argparse
import asyncio
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--script-file', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--voice-gender', default='female', choices=['female', 'male'])
    args = parser.parse_args()

    script_file_path = args.script_file.strip('"\'')
    output_path = args.output.strip('"\'')
    gender = (args.voice_gender or 'female').lower()

    with open(script_file_path, encoding='utf-8') as source:
        text = source.read().strip()

    if not text:
        raise ValueError('Narration script is empty.')

    # 1. Primary Engine: edge-tts (High-Definition Neural Male & Female news voices)
    try:
        import edge_tts
        voice = 'en-US-ChristopherNeural' if gender == 'male' else 'en-US-JennyNeural'

        async def generate_edge():
            communicate = edge_tts.Communicate(text, voice, rate="-3%")
            mp3_out = str(Path(output_path).with_suffix('.mp3'))
            await communicate.save(mp3_out)

            try:
                import imageio_ffmpeg
                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                ffmpeg = 'ffmpeg'

            subprocess.run(
                [ffmpeg, '-y', '-i', mp3_out, '-ac', '1', '-ar', '24000', output_path],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            Path(mp3_out).unlink(missing_ok=True)

        asyncio.run(generate_edge())
        if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
            print(f"Generated {gender} TTS using edge-tts ({voice})")
            return
    except Exception as e:
        print(f"edge-tts unavailable or failed: {e}")

    # 2. Secondary Engine: Kokoro TTS
    try:
        from kokoro import KPipeline
        import numpy as np
        import soundfile as sf
        kokoro_voice = 'am_michael' if gender == 'male' else 'af_heart'
        pipeline = KPipeline(lang_code='a')
        segments = [audio for _, _, audio in pipeline(text, voice=kokoro_voice, speed=0.96)]
        if segments:
            sf.write(output_path, np.concatenate(segments), 24000)
            print(f"Generated {gender} TTS using Kokoro ({kokoro_voice})")
            return
    except Exception as e:
        print(f"Kokoro failed: {e}")

    # 3. Fallback Engine: gTTS with FFmpeg male pitch shift
    try:
        from gtts import gTTS
        tld = 'co.uk' if gender == 'male' else 'com'
        tts = gTTS(text=text, lang='en', tld=tld)
        mp3_out = str(Path(output_path).with_suffix('.mp3'))
        tts.save(mp3_out)

        try:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ffmpeg = 'ffmpeg'

        # If male, apply pitch shift with ffmpeg filter to guarantee deep baritone tone
        audio_filter = "asetrate=24000*0.80,aresample=24000,atempo=1.25" if gender == 'male' else "anull"
        subprocess.run(
            [ffmpeg, '-y', '-i', mp3_out, '-af', audio_filter, '-ac', '1', '-ar', '24000', output_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        Path(mp3_out).unlink(missing_ok=True)
        print(f"Generated {gender} TTS using gTTS fallback")
    except Exception as e:
        raise RuntimeError(f"All TTS backends failed: {e}")


if __name__ == '__main__':
    main()






if __name__ == '__main__':
    main()
