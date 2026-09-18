"""
OmniConvert Steganographic Ownership & Watermarking Engine
===========================================================
Provides multi-tiered zero-width Unicode steganography, digital provenance signatures,
and file metadata tagging for verifying original authorship (Armaan).
"""

import hashlib
import json
import os
import re
from typing import Dict, Any, Optional

# Zero-Width Character Tokens
ZW_PREFIX = "\uFEFF"    # Zero-Width No-Break Space (Start Marker)
ZW_ZERO = "\u200B"      # Zero-Width Space ('0')
ZW_ONE = "\u200C"       # Zero-Width Non-Joiner ('1')
ZW_DELIM = "\u200D"     # Zero-Width Joiner (Delimiter)

OWNER_NAME = "Armaan"
PROJECT_NAME = "OmniConvert"
OWNER_SIGNATURE = "0x9F8B4A2C1D3E7F6A"
PROVENANCE_PAYLOAD = f"OWNER: {OWNER_NAME} | PROJECT: {PROJECT_NAME} | SIGNATURE: {OWNER_SIGNATURE}"


def text_to_zerowidth(text: str) -> str:
    """Encode an ASCII string into an invisible zero-width Unicode sequence."""
    binary_chars = []
    for char in text:
        bits = format(ord(char), '08b')
        zw_bits = "".join(ZW_ONE if bit == '1' else ZW_ZERO for bit in bits)
        binary_chars.append(zw_bits)
    return ZW_PREFIX + ZW_DELIM.join(binary_chars) + ZW_PREFIX


def zerowidth_to_text(zw_str: str) -> Optional[str]:
    """Decode an invisible zero-width Unicode sequence back to original text."""
    if ZW_PREFIX not in zw_str:
        return None
    
    # Extract portion between or starting with prefix
    pattern = f"{ZW_PREFIX}([{ZW_ZERO}{ZW_ONE}{ZW_DELIM}]+){ZW_PREFIX}?"
    match = re.search(pattern, zw_str)
    if not match:
        return None
    
    zw_payload = match.group(1)
    char_blocks = zw_payload.split(ZW_DELIM)
    decoded_chars = []
    
    for block in char_blocks:
        if not block:
            continue
        bit_str = "".join('1' if c == ZW_ONE else '0' for c in block if c in (ZW_ZERO, ZW_ONE))
        if len(bit_str) == 8:
            decoded_chars.append(chr(int(bit_str, 2)))
    
    return "".join(decoded_chars) if decoded_chars else None


def embed_zerowidth_in_line(line: str, payload: str = PROVENANCE_PAYLOAD) -> str:
    """Invisibly inject zero-width encoded payload at the end of a line."""
    zw_encoded = text_to_zerowidth(payload)
    return line + zw_encoded


def extract_watermark_from_content(content: str) -> Optional[Dict[str, Any]]:
    """Scan content (string or file content) for zero-width steganographic signatures."""
    decoded = zerowidth_to_text(content)
    if decoded and "OWNER:" in decoded:
        return {
            "valid": True,
            "raw_payload": decoded,
            "owner": OWNER_NAME,
            "project": PROJECT_NAME,
            "signature": OWNER_SIGNATURE
        }
    return None


def get_provenance_info() -> Dict[str, Any]:
    """Return explicit and steganographic provenance metadata."""
    zw_token = text_to_zerowidth(PROVENANCE_PAYLOAD)
    signature_hash = hashlib.sha256(PROVENANCE_PAYLOAD.encode('utf-8')).hexdigest()
    return {
        "owner": OWNER_NAME,
        "project": PROJECT_NAME,
        "signature_id": OWNER_SIGNATURE,
        "sha256": signature_hash,
        "zerowidth_token": zw_token,
        "provenance_header": f"{PROJECT_NAME} ({OWNER_NAME})"
    }


def watermark_file_bytes(content_bytes: bytes, filename: str) -> bytes:
    """Invisibly embed owner fingerprint into output binary streams where appropriate."""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    
    # 1. JSON / Data files
    if ext in ("json", "geojson"):
        try:
            data = json.loads(content_bytes.decode('utf-8'))
            if isinstance(data, dict):
                # Add non-intrusive metadata key
                data["_provenance"] = {
                    "owner": OWNER_NAME,
                    "engine": PROJECT_NAME,
                    "token": text_to_zerowidth(PROVENANCE_PAYLOAD)
                }
                return json.dumps(data, indent=2).encode('utf-8')
        except Exception:
            pass
            
    # 2. Text / Markdown / HTML files
    elif ext in ("txt", "md", "html", "htm", "css", "js", "py", "sql", "xml", "csv"):
        try:
            text = content_bytes.decode('utf-8')
            zw_marker = text_to_zerowidth(PROVENANCE_PAYLOAD)
            if ext == "html" or ext == "htm":
                # Inject inside HTML comment
                watermarked = f"<!-- {PROJECT_NAME} Engine {zw_marker} -->\n" + text
            elif ext in ("py", "sh", "sql"):
                watermarked = f"# {PROJECT_NAME} Engine {zw_marker}\n" + text
            elif ext in ("js", "css"):
                watermarked = f"/* {PROJECT_NAME} Engine {zw_marker} */\n" + text
            else:
                watermarked = text + f"\n{zw_marker}"
            return watermarked.encode('utf-8')
        except Exception:
            pass
            
    return content_bytes
