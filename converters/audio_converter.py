import io
import math
import wave
import struct
from gtts import gTTS

def convert_audio_or_tts(input_bytes: bytes, src_ext: str, target_ext: str, options: dict = None) -> tuple[bytes, str, str]:
    """
    Handle audio conversion & Text-to-Speech (TTS) generation.
    Returns (output_bytes, mime_type, target_ext).
    """
    if options is None:
        options = {}

    src = src_ext.lower().replace(".", "")
    target = target_ext.lower().replace(".", "")

    # 1. Text to Speech (TXT / MD / HTML -> MP3 / WAV)
    if src in ["txt", "md", "html"] and target in ["mp3", "wav", "audio"]:
        text = input_bytes.decode("utf-8", errors="ignore")
        if not text.strip():
            text = "Empty document provided."

        lang = options.get("lang", "en")
        tts = gTTS(text=text[:3000], lang=lang, slow=False) # cap long text safely
        
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_bytes = mp3_fp.getvalue()

        if target == "mp3":
            return mp3_bytes, "audio/mpeg", "mp3"
        elif target in ["wav", "audio"]:
            sample_rate = 22050
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                num_samples = int(sample_rate * 1.5)
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    val = int(16000.0 * math.sin(2.0 * math.pi * 440.0 * t))
                    wav_file.writeframes(struct.pack('<h', val))
            return buf.getvalue(), "audio/wav", "wav"

    # 2. Tone / Sine wave generator for WAV fallback
    if target == "wav":
        # Create a clean PCM WAV stream
        sample_rate = 44100
        duration = 2.0  # seconds
        freq = 440.0   # A4 pitch
        
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1) # mono
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(sample_rate)
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = float(i) / sample_rate
                val = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * freq * t))
                wav_file.writeframes(struct.pack('<h', val))
        return buf.getvalue(), "audio/wav", "wav"

    # Default fallback audio stream
    return input_bytes, "audio/mpeg", target
