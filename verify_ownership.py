#!/usr/bin/env python3
"""
OmniConvert Steganographic Ownership Verification CLI
======================================================
Scans source files, live HTTP server endpoints, or generated output files
to extract and verify zero-width steganographic signatures proving original authorship (Armaan).
"""

import sys
import os
import argparse
import urllib.request
import json
from pathlib import Path

# Force UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters.watermark import (
    extract_watermark_from_content,
    get_provenance_info,
    OWNER_NAME,
    PROJECT_NAME,
    OWNER_SIGNATURE
)

BANNER = r"""
  ___mniConvert Ownership Verification Engine
  ===========================================
  Author: Armaan
  Project: OmniConvert Universal File Converter
"""


def verify_file(filepath: str) -> bool:
    """Scan a source or generated file for zero-width watermark."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return False

    print(f"🔍 Inspecting file: [ {path.name} ] ({path.stat().st_size} bytes)...")
    
    try:
        # Try reading as text
        content = path.read_text(encoding='utf-8', errors='ignore')
        result = extract_watermark_from_content(content)
        if result:
            print("✅ STEGANOGRAPHIC WATERMARK DETECTED!")
            print(f"   • Owner:     {result['owner']}")
            print(f"   • Project:   {result['project']}")
            print(f"   • Signature: {result['signature']}")
            print(f"   • Raw:       {result['raw_payload']}")
            return True
            
        # Check JSON structure
        if path.suffix.lower() == ".json":
            data = json.loads(content)
            if isinstance(data, dict) and "_provenance" in data:
                prov = data["_provenance"]
                print("✅ METADATA PROVENANCE TAG DETECTED!")
                print(f"   • Owner:   {prov.get('owner')}")
                print(f"   • Engine:  {prov.get('engine')}")
                return True

    except Exception as e:
        print(f"⚠️  Error scanning file: {e}")

    print("❌ No zero-width steganographic watermark found in file.")
    return False


def verify_directory(dirpath: str) -> int:
    """Scan all source files in a directory for ownership watermarks."""
    path = Path(dirpath)
    if not path.exists():
        print(f"❌ Directory not found: {dirpath}")
        return 0

    print(f"🔍 Scanning directory for steganographic provenance: {dirpath}...\n")
    found_count = 0
    scanned_count = 0

    extensions = {".py", ".js", ".html", ".css", ".md", ".json"}
    
    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix in extensions:
            if "__pycache__" in str(file_path) or ".git" in str(file_path):
                continue
            scanned_count += 1
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            result = extract_watermark_from_content(content)
            rel_path = file_path.relative_to(path)
            if result:
                found_count += 1
                print(f"  ✅ [WATERMARKED] {rel_path} -> Owner: {result['owner']} ({result['signature']})")
            else:
                print(f"  ⚪ [Clean Code ] {rel_path}")

    print(f"\n📊 Summary: {found_count} of {scanned_count} files contain verified steganographic ownership marks.")
    return found_count


def verify_live_url(url: str) -> bool:
    """Check a live running OmniConvert server endpoint for provenance headers/JSON."""
    print(f"🌐 Querying live server endpoint: {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OmniConvert-Verifier/1.0"})
        with urllib.request.urlopen(req) as resp:
            headers = resp.headers
            body_bytes = resp.read()
            body_text = body_bytes.decode('utf-8', errors='ignore')
            
            # Check custom provenance header or zero-width watermark in body/header
            prov_header = headers.get("X-OmniConvert-Provenance") or headers.get("X-Powered-By")
            zw_in_body = extract_watermark_from_content(body_text)
            
            if prov_header or zw_in_body:
                print("✅ LIVE SERVER OWNERSHIP VERIFIED!")
                if prov_header:
                    print(f"   • Provenance Header: {prov_header}")
                if zw_in_body:
                    print(f"   • Steganographic Payload: {zw_in_body['raw_payload']}")
                return True
            
            # Try JSON body
            try:
                data = json.loads(body_text)
                if isinstance(data, dict) and data.get("owner") == OWNER_NAME:
                    print("✅ PROVENANCE ENDPOINT CONFIRMED AUTHOR!")
                    print(f"   • Owner: {data.get('owner')}")
                    print(f"   • Project: {data.get('project')}")
                    return True
            except Exception:
                pass
                
    except Exception as e:
        print(f"❌ Failed to reach or verify URL: {e}")
        return False
        
    print("❌ Live endpoint did not exhibit ownership watermark.")
    return False


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="OmniConvert Steganographic Ownership Verification")
    parser.add_argument("--file", "-f", help="Path to a single file to inspect")
    parser.add_argument("--dir", "-d", help="Path to workspace directory to scan", default=".")
    parser.add_argument("--url", "-u", help="URL of live running OmniConvert server (e.g., http://localhost:8000/api/provenance)")
    parser.add_argument("--info", "-i", action="store_true", help="Print explicit provenance signature details")

    args = parser.parse_args()

    if args.info:
        info = get_provenance_info()
        print("📜 Cryptographic Ownership Certificate:")
        print(f"   • Author & Owner:  {info['owner']}")
        print(f"   • Project Name:    {info['project']}")
        print(f"   • Signature ID:    {info['signature_id']}")
        print(f"   • SHA256 Hash:     {info['sha256']}")
        print(f"   • Provenance Tag:  {info['provenance_header']}")
        return

    if args.file:
        verify_file(args.file)
    elif args.url:
        verify_live_url(args.url)
    else:
        verify_directory(args.dir)


if __name__ == "__main__":
    main()
