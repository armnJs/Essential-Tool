import io
import re
import json
import yaml
import base64
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd

def dict_to_xml(d, root_tag="root"):
    """Convert dict to XML element tree string"""
    def _to_xml(data, parent):
        if isinstance(data, dict):
            for k, v in data.items():
                # Sanitize XML key
                k_clean = str(k).replace(" ", "_").replace("-", "_")
                child = ET.SubElement(parent, k_clean)
                _to_xml(v, child)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, "item")
                _to_xml(item, child)
        else:
            parent.text = str(data)

    root = ET.Element(root_tag)
    _to_xml(d, root)
    xml_str = ET.tostring(root, encoding="utf-8")
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent="  ")

def xml_to_dict(xml_str):
    """Convert XML string to dict"""
    root = ET.fromstring(xml_str)
    def _xml_to_dict(node):
        d = {}
        for child in node:
            if len(child) > 0:
                child_d = _xml_to_dict(child)
            else:
                child_d = child.text
            if child.tag in d:
                if isinstance(d[child.tag], list):
                    d[child.tag].append(child_d)
                else:
                    d[child.tag] = [d[child.tag], child_d]
            else:
                d[child.tag] = child_d
        return d or node.text
    return {root.tag: _xml_to_dict(root)}

def convert_data(input_bytes: bytes, src_ext: str, target_ext: str, options: dict = None) -> tuple[bytes, str, str]:
    """
    Convert data / format files (json, yaml, xml, csv, tsv, base64, sql, py).
    Returns (output_bytes, mime_type, target_ext).
    """
    if options is None:
        options = {}

    src = src_ext.lower().replace(".", "")
    target = target_ext.lower().replace(".", "")

    text_input = input_bytes.decode("utf-8", errors="ignore")

    # Handle Base64 conversions
    if target == "base64":
        b64 = base64.b64encode(input_bytes).decode("utf-8")
        return b64.encode("utf-8"), "text/plain", "txt"
    if src == "base64":
        raw = base64.b64decode(text_input.strip())
        return raw, "application/octet-stream", target

    # Parse input into intermediate structure (python dict / list)
    parsed_data = None
    if src == "json":
        parsed_data = json.loads(text_input)
    elif src in ["yaml", "yml"]:
        parsed_data = yaml.safe_load(text_input)
    elif src == "xml":
        parsed_data = xml_to_dict(text_input)
    elif src in ["csv", "tsv"]:
        sep = "\t" if src == "tsv" else ","
        df = pd.read_csv(io.StringIO(text_input), sep=sep)
        parsed_data = df.to_dict(orient="records")
    else:
        # Fallback raw text wrapper
        parsed_data = {"content": text_input}

    # Format to target
    if target == "json":
        out_str = json.dumps(parsed_data, indent=2, ensure_ascii=False)
        return out_str.encode("utf-8"), "application/json", "json"
    elif target in ["yaml", "yml"]:
        out_str = yaml.dump(parsed_data, sort_keys=False, allow_unicode=True)
        return out_str.encode("utf-8"), "text/yaml", "yaml"
    elif target == "xml":
        out_str = dict_to_xml(parsed_data)
        return out_str.encode("utf-8"), "application/xml", "xml"
    elif target in ["csv", "tsv"]:
        sep = "\t" if target == "tsv" else ","
        if isinstance(parsed_data, list) and all(isinstance(i, dict) for i in parsed_data):
            df = pd.DataFrame(parsed_data)
        else:
            df = pd.json_normalize(parsed_data)
        out_str = df.to_csv(index=False, sep=sep)
        mime = "text/tab-separated-values" if target == "tsv" else "text/csv"
        return out_str.encode("utf-8"), mime, target
    elif target == "xlsx":
        if isinstance(parsed_data, list) and all(isinstance(i, dict) for i in parsed_data):
            df = pd.DataFrame(parsed_data)
        else:
            df = pd.json_normalize(parsed_data)
        out_buf = io.BytesIO()
        with pd.ExcelWriter(out_buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return out_buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
    elif target == "sql":
        raw_table_name = options.get("table_name", "data_table")
        clean_tokens = [t for t in re.split(r'[^a-zA-Z0-9_]', str(raw_table_name)) if t]
        table_name = clean_tokens[0] if clean_tokens else "data_table"
        if isinstance(parsed_data, list) and all(isinstance(i, dict) for i in parsed_data):
            statements = []
            for row in parsed_data:
                cols = ", ".join([f"`{re.sub(r'[^a-zA-Z0-9_]', '', str(k))}`" for k in row.keys()])
                vals = ", ".join([f"'{str(v).replace("'", "''")}'" for v in row.values()])
                statements.append(f"INSERT INTO `{table_name}` ({cols}) VALUES ({vals});")
            out_str = "\n".join(statements)
        else:
            out_str = f"-- SQL representation for {table_name}\n" + json.dumps(parsed_data)
        return out_str.encode("utf-8"), "text/plain", "sql"
    elif target == "py":
        out_str = f"data = {json.dumps(parsed_data, indent=4)}\n"
        return out_str.encode("utf-8"), "text/x-python", "py"

    raise ValueError(f"Unsupported data conversion from .{src} to .{target}")
