import io
import os
import re
import pandas as pd
from PIL import Image
import docx
import markdown as md_lib
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pypdf

import json

def parse_ipynb(input_bytes: bytes) -> tuple[str, list[dict]]:
    """Parse Jupyter Notebook .ipynb bytes into formatted text and structured cells."""
    data = json.loads(input_bytes.decode("utf-8", errors="ignore"))
    cells = data.get("cells", [])
    
    markdown_chunks = []
    structured_cells = []
    
    for idx, cell in enumerate(cells, 1):
        cell_type = cell.get("cell_type", "code")
        source = cell.get("source", [])
        if isinstance(source, list):
            source_text = "".join(source)
        else:
            source_text = str(source)
            
        outputs_text = []
        if cell_type == "code":
            for out in cell.get("outputs", []):
                if "text" in out:
                    t = out["text"]
                    outputs_text.append("".join(t) if isinstance(t, list) else str(t))
                elif "data" in out and "text/plain" in out["data"]:
                    tp = out["data"]["text/plain"]
                    outputs_text.append("".join(tp) if isinstance(tp, list) else str(tp))
                    
        structured_cells.append({
            "index": idx,
            "type": cell_type,
            "source": source_text,
            "outputs": "\n".join(outputs_text)
        })
        
        if cell_type == "markdown":
            markdown_chunks.append(source_text)
        elif cell_type == "code":
            code_block = f"```python\n# [In {idx}]\n{source_text}\n```"
            if outputs_text:
                out_block = "\n".join(outputs_text)
                code_block += f"\n\n*Output:*\n```\n{out_block}\n```"
            markdown_chunks.append(code_block)
            
    full_markdown = "\n\n".join(markdown_chunks)
    return full_markdown, structured_cells


def create_ipynb_bytes(source_text: str, is_code: bool = True) -> bytes:
    """Create Jupyter Notebook (.ipynb) bytes from input source text."""
    lines = source_text.splitlines(keepends=True)
    cells = []
    
    if is_code:
        chunk = []
        for line in lines:
            if line.startswith("# %%") or line.startswith("# [In"):
                if chunk:
                    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": chunk})
                    chunk = []
            chunk.append(line)
        if chunk:
            cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": chunk})
    else:
        cells.append({"cell_type": "markdown", "metadata": {}, "source": lines})

    nb_data = {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python"},
            "orig_nbformat": 4
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    return json.dumps(nb_data, indent=2, ensure_ascii=False).encode("utf-8")


def convert_document(input_bytes: bytes, src_ext: str, target_ext: str, options: dict = None) -> tuple[bytes, str, str]:
    """
    Convert document between formats.
    Returns (output_bytes, mime_type, suggested_filename_suffix).
    """
    if options is None:
        options = {}

    src = src_ext.lower().replace(".", "")
    target = target_ext.lower().replace(".", "")

    # Convert PY / MD / TXT / HTML / JSON -> IPYNB (Jupyter Notebook)
    if target == "ipynb":
        text_content = input_bytes.decode("utf-8", errors="ignore")
        is_code = src in ["py", "python", "json", "sql"]
        nb_bytes = create_ipynb_bytes(text_content, is_code=is_code)
        return nb_bytes, "application/json", "ipynb"

    # Jupyter Notebook (.ipynb) Conversions
    if src == "ipynb":
        full_md, cells = parse_ipynb(input_bytes)
        
        if target == "py":
            py_code = []
            for cell in cells:
                if cell["type"] == "code":
                    py_code.append(f"# %% [In {cell['index']}]\n{cell['source']}\n")
            py_text = "\n".join(py_code)
            return py_text.encode("utf-8"), "text/x-python", "py"
            
        if target == "md":
            return full_md.encode("utf-8"), "text/markdown", "md"
            
        if target == "txt":
            txt_lines = []
            for cell in cells:
                txt_lines.append(f"--- Cell {cell['index']} ({cell['type']}) ---")
                txt_lines.append(cell["source"])
                if cell["outputs"]:
                    txt_lines.append(f"[Output]:\n{cell['outputs']}")
                txt_lines.append("")
            return "\n".join(txt_lines).encode("utf-8"), "text/plain", "txt"
            
        if target == "html":
            html_parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>Jupyter Notebook</title>",
                          "<style>body{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#1e293b;}",
                          "pre{background:#f1f5f9;padding:1rem;border-radius:8px;overflow-x:auto;border:1px solid #cbd5e1;font-family:monospace;}",
                          ".cell-code{background:#f8fafc;border-left:4px solid #6366f1;margin:1.5rem 0;padding:1rem;border-radius:0 8px 8px 0;}",
                          ".cell-output{background:#0f172a;color:#38bdf8;padding:0.75rem;border-radius:6px;font-family:monospace;font-size:0.9rem;margin-top:0.5rem;}",
                          "</style></head><body>", "<h1>Jupyter Notebook Export</h1>"]
            for cell in cells:
                if cell["type"] == "markdown":
                    html_parts.append(f"<div>{md_lib.markdown(cell['source'])}</div>")
                else:
                    code_escaped = cell["source"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    html_parts.append(f"<div class='cell-code'><strong>In [{cell['index']}]:</strong><pre><code>{code_escaped}</code></pre>")
                    if cell["outputs"]:
                        out_escaped = cell["outputs"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        html_parts.append(f"<div class='cell-output'><strong>Output:</strong><pre>{out_escaped}</pre></div>")
                    html_parts.append("</div>")
            html_parts.append("</body></html>")
            return "".join(html_parts).encode("utf-8"), "text/html", "html"
            
        if target == "docx":
            doc = docx.Document()
            doc.add_heading("Jupyter Notebook Export", level=1)
            for cell in cells:
                if cell["type"] == "markdown":
                    doc.add_paragraph(cell["source"])
                else:
                    p = doc.add_paragraph()
                    p.add_run(f"In [{cell['index']}]:").bold = True
                    p_code = doc.add_paragraph(cell["source"])
                    p_code.style = 'Quote'
                    if cell["outputs"]:
                        p_out = doc.add_paragraph(f"Output:\n{cell['outputs']}")
                        p_out.style = 'List Bullet'
            buffer = io.BytesIO()
            doc.save(buffer)
            return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"
            
        if target == "pdf":
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
            styles = getSampleStyleSheet()
            normal = styles['Normal']
            normal.leading = 14
            story = [Paragraph("<b>Jupyter Notebook Document</b>", styles['Heading1']), Spacer(1, 12)]
            
            for cell in cells:
                if cell["type"] == "markdown":
                    for line in cell["source"].splitlines():
                        if line.strip():
                            clean_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            story.append(Paragraph(clean_line, normal))
                            story.append(Spacer(1, 4))
                else:
                    code_hdr = f"<b>In [{cell['index']}]:</b>"
                    story.append(Paragraph(code_hdr, normal))
                    clean_code = cell["source"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                    story.append(Paragraph(f"<font color='#4338ca'><code>{clean_code}</code></font>", normal))
                    if cell["outputs"]:
                        clean_out = cell["outputs"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                        story.append(Paragraph(f"<font color='#0284c7'>Output: {clean_out}</font>", normal))
                    story.append(Spacer(1, 10))
                    
            doc.build(story)
            return buffer.getvalue(), "application/pdf", "pdf"

    # MD / TXT -> HTML
    if src in ["md", "txt"] and target == "html":
        text_content = input_bytes.decode("utf-8", errors="ignore")
        if src == "md":
            body = md_lib.markdown(text_content, extensions=['fenced_code', 'tables'])
        else:
            lines = [f"<p>{line}</p>" for line in text_content.splitlines() if line]
            body = "\n".join(lines)
        html = f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{body}</body></html>"
        return html.encode("utf-8"), "text/html", "html"

    # 1. Images to PDF
    if src in ["png", "jpg", "jpeg", "webp", "bmp"] and target == "pdf":

        img = Image.open(io.BytesIO(input_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PDF")
        return out.getvalue(), "application/pdf", "pdf"

    # 2. Text / Markdown / HTML -> PDF via ReportLab
    if src in ["txt", "md", "html"] and target == "pdf":
        text_content = input_bytes.decode("utf-8", errors="ignore")
        if src == "md":
            html_content = md_lib.markdown(text_content)
        elif src == "txt":
            # Wrap plain text into html paragraphs
            lines = text_content.splitlines()
            html_content = "".join([f"<p>{line if line else '&nbsp;'}</p>" for line in lines])
        else:
            html_content = text_content

        soup = BeautifulSoup(html_content, "html.parser")
        plain_text = soup.get_text()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        normal = styles['Normal']
        normal.leading = 14
        
        story = []
        for paragraph in plain_text.split('\n'):
            if paragraph.strip():
                # Escape XML characters for reportlab
                clean_p = paragraph.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(clean_p, normal))
                story.append(Spacer(1, 8))

        doc.build(story)
        return buffer.getvalue(), "application/pdf", "pdf"

    # 3. TXT / Markdown / HTML -> DOCX
    if src in ["txt", "md", "html"] and target in ["docx", "doc"]:
        text_content = input_bytes.decode("utf-8", errors="ignore")
        doc = docx.Document()
        if src == "md":
            lines = text_content.splitlines()
            for line in lines:
                if line.startswith("# "):
                    doc.add_heading(line[2:], level=1)
                elif line.startswith("## "):
                    doc.add_heading(line[3:], level=2)
                elif line.startswith("### "):
                    doc.add_heading(line[4:], level=3)
                elif line.startswith("- ") or line.startswith("* "):
                    doc.add_paragraph(line[2:], style='List Bullet')
                else:
                    doc.add_paragraph(line)
        elif src == "html":
            soup = BeautifulSoup(text_content, "html.parser")
            for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                doc.add_paragraph(p.get_text())
        else:
            doc.add_paragraph(text_content)

        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"

    # 4. DOCX -> TXT / HTML / MD
    if src in ["docx", "doc"] and target in ["txt", "html", "md"]:
        doc = docx.Document(io.BytesIO(input_bytes))
        paragraphs = [p.text for p in doc.paragraphs]
        
        if target == "txt":
            res = "\n".join(paragraphs)
            return res.encode("utf-8"), "text/plain", "txt"
        elif target == "md":
            res = "\n\n".join(paragraphs)
            return res.encode("utf-8"), "text/markdown", "md"
        elif target == "html":
            body = "".join([f"<p>{p}</p>" for p in paragraphs])
            html = f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>{body}</body></html>"
            return html.encode("utf-8"), "text/html", "html"

    # 5. PDF -> TXT / Extract Text
    if src == "pdf" and target in ["txt", "md", "html"]:
        reader = pypdf.PdfReader(io.BytesIO(input_bytes))
        text_pages = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            text_pages.append(f"--- Page {i+1} ---\n{txt}")
        
        full_text = "\n\n".join(text_pages)
        if target == "html":
            body = "".join([f"<h3>Page {i+1}</h3><pre>{page}</pre>" for i, page in enumerate(text_pages)])
            full_text = f"<!DOCTYPE html><html><body>{body}</body></html>"

        mime = "text/plain" if target in ["txt", "md"] else "text/html"
        return full_text.encode("utf-8"), mime, target

    # HTML -> MD / TXT
    if src == "html" and target in ["md", "txt"]:
        text_content = input_bytes.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(text_content, "html.parser")
        headings = [f"# {h.get_text()}" for h in soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.get_text() for p in soup.find_all(['p', 'li'])]
        md_text = "\n\n".join(headings + paragraphs) or soup.get_text()
        return md_text.encode("utf-8"), "text/markdown" if target == "md" else "text/plain", target

    # 6. CSV / Excel XLSX / Data sheet conversions
    if src in ["csv", "xlsx", "xls", "json"] and target in ["csv", "xlsx", "json", "html", "md"]:
        buffer_in = io.BytesIO(input_bytes)
        if src == "csv":
            df = pd.read_csv(buffer_in)
        elif src in ["xlsx", "xls"]:
            try:
                df = pd.read_excel(buffer_in, engine='openpyxl')
            except Exception as e:
                raise ValueError("Invalid or corrupted XLSX file provided.")
        elif src == "json":
            df = pd.read_json(buffer_in)
        else:
            raise ValueError(f"Cannot parse input data sheet {src}")

        buffer_out = io.BytesIO()
        if target == "csv":
            df.to_csv(buffer_out, index=False)
            return buffer_out.getvalue(), "text/csv", "csv"
        elif target == "xlsx":
            with pd.ExcelWriter(buffer_out, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return buffer_out.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
        elif target == "json":
            json_str = df.to_json(orient="records", indent=2)
            return json_str.encode("utf-8"), "application/json", "json"
        elif target == "html":
            html_str = df.to_html(index=False, classes="table table-striped")
            return html_str.encode("utf-8"), "text/html", "html"
        elif target == "md":
            md_str = df.to_markdown(index=False)
            return md_str.encode("utf-8"), "text/markdown", "md"

    raise ValueError(f"Unsupported document conversion from .{src} to .{target}")
