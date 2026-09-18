import sys
import os
import json
from converters.registry import process_conversion, get_allowed_targets

def run_tests():
    print("=== Running OmniConvert Test Suite ===")

    # Test 1: Image Conversion (Create a small 10x10 PNG image)
    from PIL import Image
    import io
    img_buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(img_buf, format="PNG")
    png_bytes = img_buf.getvalue()

    print("[TEST 1] Testing PNG -> JPG & WEBP...")
    jpg_out, mime_jpg, filename_jpg = process_conversion(png_bytes, "test.png", "jpg")
    assert len(jpg_out) > 0 and mime_jpg == "image/jpeg"
    print(f" -> PASSED: Created {filename_jpg} ({len(jpg_out)} bytes)")

    webp_out, mime_webp, filename_webp = process_conversion(png_bytes, "test.png", "webp")
    assert len(webp_out) > 0 and mime_webp == "image/webp"
    print(f" -> PASSED: Created {filename_webp} ({len(webp_out)} bytes)")

    # Test 2: Data Conversion (JSON -> CSV, YAML, XML, SQL)
    print("\n[TEST 2] Testing JSON -> CSV, YAML, XML & SQL...")
    sample_json = json.dumps([
        {"id": 1, "name": "Alice", "role": "Developer"},
        {"id": 2, "name": "Bob", "role": "Designer"}
    ]).encode("utf-8")

    csv_out, mime_csv, filename_csv = process_conversion(sample_json, "users.json", "csv")
    assert b"Alice" in csv_out and b"Developer" in csv_out
    print(f" -> PASSED: Created {filename_csv}")

    yaml_out, mime_yaml, filename_yaml = process_conversion(sample_json, "users.json", "yaml")
    assert b"Alice" in yaml_out
    print(f" -> PASSED: Created {filename_yaml}")

    sql_out, mime_sql, filename_sql = process_conversion(sample_json, "users.json", "sql", {"table_name": "users"})
    assert b"INSERT INTO `users`" in sql_out
    print(f" -> PASSED: Created {filename_sql}")

    # Test 3: Document Conversion (TXT -> PDF, HTML -> PDF)
    print("\n[TEST 3] Testing Text/HTML -> PDF...")
    sample_txt = b"Hello World! This is a test document conversion for OmniConvert."
    pdf_out, mime_pdf, filename_pdf = process_conversion(sample_txt, "doc.txt", "pdf")
    assert len(pdf_out) > 0 and mime_pdf == "application/pdf"
    print(f" -> PASSED: Created {filename_pdf} ({len(pdf_out)} bytes)")

    # Test 4: Archive (TXT -> ZIP)
    print("\n[TEST 4] Testing File -> ZIP Archive...")
    zip_out, mime_zip, filename_zip = process_conversion(sample_txt, "notes.txt", "zip")
    assert len(zip_out) > 0 and mime_zip == "application/zip"
    print(f" -> PASSED: Created {filename_zip} ({len(zip_out)} bytes)")

    # Test 5: Jupyter Notebook (.ipynb -> PDF, DOCX, HTML, PY)
    print("\n[TEST 5] Testing Jupyter Notebook (.ipynb) -> PDF, DOCX, HTML & PY...")
    sample_ipynb = json.dumps({
        "cells": [
            {"cell_type": "markdown", "source": ["# Analysis Notebook\n", "This notebook demonstrates data visualization."]},
            {"cell_type": "code", "source": ["import numpy as np\n", "print('Hello Jupyter!')"], "outputs": [{"text": ["Hello Jupyter!\n"]}]}
        ]
    }).encode("utf-8")

    pdf_nb, mime_pdf_nb, fn_pdf_nb = process_conversion(sample_ipynb, "analysis.ipynb", "pdf")
    assert len(pdf_nb) > 0 and mime_pdf_nb == "application/pdf"
    print(f" -> PASSED: Created {fn_pdf_nb} ({len(pdf_nb)} bytes)")

    docx_nb, mime_docx_nb, fn_docx_nb = process_conversion(sample_ipynb, "analysis.ipynb", "docx")
    assert len(docx_nb) > 0 and "officedocument" in mime_docx_nb
    print(f" -> PASSED: Created {fn_docx_nb} ({len(docx_nb)} bytes)")

    py_nb, mime_py_nb, fn_py_nb = process_conversion(sample_ipynb, "analysis.ipynb", "py")
    assert b"import numpy as np" in py_nb
    print(f" -> PASSED: Created {fn_py_nb}")

    print("\n==========================================")

    print("ALL CONVERTER TESTS PASSED SUCCESSFULLY! ")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
