import io
import json
import unittest
from PIL import Image
from fastapi.testclient import TestClient

from server import app
from converters.image_converter import convert_image
from converters.doc_converter import convert_document
from converters.data_converter import convert_data
from converters.audio_converter import convert_audio_or_tts
from converters.archive_converter import convert_archive
from converters.video_converter import convert_video
from converters.registry import process_conversion, get_allowed_targets


class TestOmniConvertSuite(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    # ----------------------------------------------------
    # 1. Image & iOS Image Converter Tests
    # ----------------------------------------------------
    def test_image_png_to_jpg(self):
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        out_bytes, mime, ext = convert_image(png_bytes, "png", "jpg", {"quality": 90, "grayscale": True})
        self.assertEqual(mime, "image/jpeg")
        self.assertEqual(ext, "jpg")
        self.assertGreater(len(out_bytes), 0)

        out_img = Image.open(io.BytesIO(out_bytes))
        self.assertEqual(out_img.format, "JPEG")
        self.assertEqual(out_img.mode, "L")  # Grayscale

    def test_ios_heic_image_conversion(self):
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        out_bytes, mime, ext = convert_image(png_bytes, "heic", "png")
        self.assertEqual(mime, "image/png")
        self.assertEqual(ext, "png")

    # ----------------------------------------------------
    # 2. Document & iWork Tests
    # ----------------------------------------------------
    def test_doc_txt_to_pdf(self):
        txt_bytes = b"Hello OmniConvert World!\nThis is a PDF test document."
        out_bytes, mime, ext = convert_document(txt_bytes, "txt", "pdf")
        self.assertEqual(mime, "application/pdf")
        self.assertEqual(ext, "pdf")
        self.assertTrue(out_bytes.startswith(b"%PDF"))

    def test_ipynb_to_py(self):
        nb_dict = {
            "cells": [
                {"cell_type": "markdown", "source": ["# Header\n", "Intro text"]},
                {"cell_type": "code", "source": ["x = 10\n", "print(x)"]}
            ]
        }
        nb_bytes = json.dumps(nb_dict).encode("utf-8")
        out_bytes, mime, ext = convert_document(nb_bytes, "ipynb", "py")
        self.assertEqual(ext, "py")
        py_text = out_bytes.decode("utf-8")
        self.assertIn("x = 10", py_text)
        self.assertIn("# Header", py_text)

    # ----------------------------------------------------
    # 3. Data & Apple iOS Data Tests (PLIST, VCF, TOML, Parquet)
    # ----------------------------------------------------
    def test_json_to_yaml_and_sql(self):
        json_bytes = b'[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'

        out_yaml, mime, ext = convert_data(json_bytes, "json", "yaml")
        self.assertEqual(ext, "yaml")
        self.assertIn("name: Alice", out_yaml.decode("utf-8"))

        out_sql, mime, ext = convert_data(json_bytes, "json", "sql", {"table_name": "users"})
        self.assertEqual(ext, "sql")
        sql_text = out_sql.decode("utf-8")
        self.assertIn("INSERT INTO `users`", sql_text)

    def test_apple_plist_conversion(self):
        json_bytes = b'{"Author": "Armaan", "App": "OmniConvert"}'
        out_plist, mime, ext = convert_data(json_bytes, "json", "plist")
        self.assertEqual(ext, "plist")
        self.assertIn("<plist", out_plist.decode("utf-8"))


    def test_apple_vcard_vcf_conversion(self):
        vcf_bytes = b"BEGIN:VCARD\nVERSION:3.0\nFN:Armaan\nTEL:1234567890\nEND:VCARD"
        out_json, mime, ext = convert_data(vcf_bytes, "vcf", "json")
        self.assertEqual(ext, "json")
        self.assertIn("Armaan", out_json.decode("utf-8"))

    # ----------------------------------------------------
    # 4. Audio & iOS Media Tests
    # ----------------------------------------------------
    def test_audio_m4a_and_tts(self):
        txt_bytes = b"Hello, iOS Audio conversion test."
        out_bytes, mime, ext = convert_audio_or_tts(txt_bytes, "txt", "m4a", {"lang": "en"})
        self.assertEqual(ext, "m4a")
        self.assertGreater(len(out_bytes), 0)

    # ----------------------------------------------------
    # 5. Archive Tests
    # ----------------------------------------------------
    def test_file_to_zip_archive(self):
        raw_bytes = b"Sample text to compress into archive."
        out_bytes, mime, ext = convert_archive(raw_bytes, "test.txt", "txt", "zip")
        self.assertEqual(mime, "application/zip")
        self.assertEqual(ext, "zip")
        self.assertTrue(out_bytes.startswith(b"PK"))

    # ----------------------------------------------------
    # 6. FastAPI Integration Route Tests
    # ----------------------------------------------------
    def test_api_health(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_api_formats(self):
        resp = self.client.get("/api/formats?src=mov")
        self.assertEqual(resp.status_code, 200)
        targets = resp.json()["allowed_targets"]
        self.assertIn("mp4", targets)
        self.assertIn("gif", targets)

    def test_api_convert_endpoint(self):
        json_payload = b'[{"city": "Cupertino", "device": "iPhone"}]'
        files = {"file": ("apple.json", io.BytesIO(json_payload), "application/json")}
        data = {"target_format": "plist", "options": "{}"}

        resp = self.client.post("/api/convert", files=files, data=data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("plist", resp.headers["content-type"])


if __name__ == "__main__":
    unittest.main()
