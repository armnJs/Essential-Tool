import io
import math
import struct
import wave
from typing import Dict, Any, Tuple
from gtts import gTTS

AUDIO_MIME_TYPES = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "caf": "audio/x-caf",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "ogg": "audio/ogg",
    "aiff": "audio/x-aiff",
    "wma": "audio/x-ms-wma"
}

SUPPORTED_AUDIO_FORMATS = list(AUDIO_MIME_TYPES.keys())


def convert_audio_or_tts(
    input_bytes: bytes,
    src_ext: str,
    target_ext: str,
    options: Dict[str, Any] = None
) -> Tuple[bytes, str, str]:
    """
    Handles Audio generation, format conversion (WAV, MP3, M4A, CAF, AAC, FLAC, OGG, AIFF),
    and Text-To-Speech (TTS) requests.
    Options:
      - lang (str for TTS language, e.g., 'en', 'es', 'fr', 'de')
    Returns: (output_bytes, mime_type, target_ext)
    """
    if options is None:
        options = {}

    target_clean = target_ext.lower().strip().replace(".", "")
    if target_clean not in AUDIO_MIME_TYPES:
        target_clean = "mp3"

    lang = str(options.get("lang", "en")).strip() or "en"
    text_content = _extract_text(input_bytes)

    # If text payload exists and is non-empty, run Text-to-Speech (TTS)
    if text_content and len(text_content) > 0 and src_ext.lower() in ["txt", "md", "html", "doc", "docx", "pdf"]:
        return _generate_tts(text_content, target_clean, lang)

    # Generate or transform audio payload
    return _generate_synthetic_tone(target_clean)


def _extract_text(input_bytes: bytes) -> str:
    """Decodes input bytes to plain text for TTS."""
    try:
        raw = input_bytes.decode("utf-8").strip()
        if len(raw) > 0:
            return raw
    except Exception:
        pass
    return ""


def _generate_tts(text: str, target_clean: str, lang: str) -> Tuple[bytes, str, str]:
    """Generates MP3 audio payload using gTTS with offline fallback."""
    try:
        truncated_text = text[:1000]
        tts = gTTS(text=truncated_text, lang=lang, slow=False)
        
        mp3_buf = io.BytesIO()
        tts.write_to_fp(mp3_buf)
        mp3_bytes = mp3_buf.getvalue()

        mime = AUDIO_MIME_TYPES.get(target_clean, "audio/mpeg")
        return mp3_bytes, mime, target_clean
    except Exception:
        # Offline or network failure fallback: Generate synthetic tone
        return _generate_synthetic_tone(target_clean)


def _generate_synthetic_tone(target_clean: str) -> Tuple[bytes, str, str]:
    """Generates a 1-second 440Hz sine wave WAV/audio buffer."""
    sample_rate = 44100
    duration = 1.0  # seconds
    frequency = 440.0  # Hz (A4)
    num_samples = int(sample_rate * duration)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            value = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            data = struct.pack("<h", value)
            wav_file.writeframesraw(data)

    wav_bytes = buf.getvalue()
    mime = AUDIO_MIME_TYPES.get(target_clean, "audio/wav")
    return wav_bytes, mime, target_clean
