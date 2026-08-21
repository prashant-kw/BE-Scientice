import argparse
import numpy as np
import soundfile as sf



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

    try:
        from kokoro import KPipeline
        kokoro_voice = 'af_heart' if gender == 'female' else 'am_michael'
        pipeline = KPipeline(lang_code='a')
        segments = [audio for _, _, audio in pipeline(text, voice=kokoro_voice, speed=0.96)]
        if not segments:
            raise RuntimeError('Kokoro produced no audio.')
        sf.write(output_path, np.concatenate(segments), 24000)
    except Exception:
        # Fallback to system pyttsx3 or gTTS if kokoro module is not installed
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            voices = engine.getProperty('voices')
            target_voice = None
            for v in voices:
                v_name = (v.name or '').lower()
                if gender == 'female' and ('female' in v_name or 'zira' in v_name or 'hazel' in v_name):
                    target_voice = v.id
                    break
                elif gender == 'male' and ('male' in v_name or 'david' in v_name or 'george' in v_name):
                    target_voice = v.id
                    break
            if target_voice:
                engine.setProperty('voice', target_voice)
            engine.save_to_file(text, output_path)
            engine.runAndWait()
        except Exception:
            from gtts import gTTS
            # gTTS accent variant for male/female feel
            tld = 'com' if gender == 'female' else 'co.uk'
            tts = gTTS(text=text, lang='en', tld=tld)
            tts.save(output_path)





if __name__ == '__main__':
    main()
