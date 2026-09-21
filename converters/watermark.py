import hashlib
import json
from typing import Optional, Dict, Any

OWNER_NAME = "Armaan (armnJs)"
PROJECT_NAME = "OmniConvert"
OWNER_SIGNATURE = "armnJs-2026-OmniConvert-0x41726d61616e"

# Zero-width Unicode characters for steganography
ZW_0 = "\u200b"  # Zero Width Space
ZW_1 = "\u200c"  # Zero Width Non-Joiner
ZW_DELIM = "\u200d"  # Zero Width Joiner

RAW_PAYLOAD = f"{OWNER_NAME}|{PROJECT_NAME}|{OWNER_SIGNATURE}"


def encode_zero_width_watermark(payload: str = RAW_PAYLOAD) -> str:
    """Encodes a string into invisible zero-width Unicode characters."""
    binary_str = "".join(format(ord(c), "08b") for c in payload)
    encoded = "".join(ZW_1 if b == "1" else ZW_0 for b in binary_str)
    return ZW_DELIM + encoded + ZW_DELIM


def decode_zero_width_watermark(text: str) -> Optional[str]:
    """Decodes zero-width Unicode characters back into plain text string."""
    if ZW_DELIM not in text:
        return None

    try:
        parts = text.split(ZW_DELIM)
        if len(parts) < 3:
            return None
        zw_content = parts[1]
        
        bits = ""
        for char in zw_content:
            if char == ZW_1:
                bits += "1"
            elif char == ZW_0:
                bits += "0"

        if not bits or len(bits) % 8 != 0:
            return None

        bytes_list = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
        return bytes(bytes_list).decode("utf-8", errors="ignore")
    except Exception:
        return None


def extract_watermark_from_content(content: str) -> Optional[Dict[str, Any]]:
    """Scans text content for zero-width watermark or returns None."""
    decoded = decode_zero_width_watermark(content)
    if decoded and "|" in decoded:
        parts = decoded.split("|")
        return {
            "owner": parts[0] if len(parts) > 0 else OWNER_NAME,
            "project": parts[1] if len(parts) > 1 else PROJECT_NAME,
            "signature": parts[2] if len(parts) > 2 else OWNER_SIGNATURE,
            "raw_payload": decoded
        }
    
    # Check if string contains plaintext owner tag
    if OWNER_NAME in content or "armnJs" in content:
        return {
            "owner": OWNER_NAME,
            "project": PROJECT_NAME,
            "signature": OWNER_SIGNATURE,
            "raw_payload": RAW_PAYLOAD
        }

    return None


def get_provenance_info() -> Dict[str, Any]:
    """Returns cryptographic provenance metadata."""
    sha256 = hashlib.sha256(RAW_PAYLOAD.encode("utf-8")).hexdigest()
    return {
        "owner": OWNER_NAME,
        "project": PROJECT_NAME,
        "signature_id": OWNER_SIGNATURE,
        "sha256": sha256,
        "provenance_header": f"X-OmniConvert-Provenance: {OWNER_NAME}",
        "zero_width_watermark": encode_zero_width_watermark()
    }
