import io
import json
import base64
import plistlib
import configparser
import xml.etree.ElementTree as ET
from typing import Dict, Any, Tuple, List, Union
import yaml
import pandas as pd

DATA_MIME_TYPES = {
    "json": "application/json",
    "yaml": "application/x-yaml",
    "yml": "application/x-yaml",
    "xml": "application/xml",
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "sql": "application/sql",
    "base64": "text/plain",
    "plist": "application/x-plist",
    "vcf": "text/vcard",
    "toml": "application/toml",
    "ndjson": "application/x-ndjson",
    "ini": "text/plain",
    "parquet": "application/vnd.apache.parquet"
}

SUPPORTED_DATA_FORMATS = list(DATA_MIME_TYPES.keys())


def convert_data(
    input_bytes: bytes,
    src_ext: str,
    target_ext: str,
    options: Dict[str, Any] = None
) -> Tuple[bytes, str, str]:
    """
    Transforms structured data including JSON, YAML, XML, CSV, TSV, SQL, Base64,
    and iOS/extended data formats (PLIST, VCF, TOML, NDJSON, INI, PARQUET).
    Options:
      - table_name (str for SQL INSERT generation, default 'data_table')
    Returns: (output_bytes, mime_type, target_ext)
    """
    if options is None:
        options = {}

    src_clean = src_ext.lower().strip().replace(".", "")
    target_clean = target_ext.lower().strip().replace(".", "")
    if src_clean == "yml":
        src_clean = "yaml"
    if target_clean == "yml":
        target_clean = "yaml"

    if target_clean not in DATA_MIME_TYPES:
        raise ValueError(f"Unsupported data target format: '{target_ext}'")

    # Handle Base64 Encoding / Decoding
    if target_clean == "base64":
        encoded = base64.b64encode(input_bytes)
        return encoded, DATA_MIME_TYPES["base64"], "base64"

    if src_clean == "base64":
        try:
            decoded = base64.b64decode(input_bytes)
            input_bytes = decoded
            src_clean = "json"
        except Exception as e:
            raise ValueError(f"Failed to decode base64 input: {e}")

    # Step 1: Parse input bytes into Python Data Structure (dict or list of dicts)
    data_obj, df = _parse_input_data(input_bytes, src_clean)

    # Step 2: Render target format
    table_name = str(options.get("table_name", "data_table")).strip() or "data_table"

    if target_clean == "plist":
        # Apple Property List Format (.plist)
        plist_bytes = _to_plist_bytes(data_obj)
        return plist_bytes, DATA_MIME_TYPES["plist"], "plist"
    elif target_clean == "vcf":
        # vCard Contacts Format (.vcf)
        vcf_str = _to_vcard_str(df if df is not None else _to_dataframe(data_obj))
        return vcf_str.encode("utf-8"), DATA_MIME_TYPES["vcf"], "vcf"
    elif target_clean == "toml":
        toml_str = _to_toml_str(data_obj)
        return toml_str.encode("utf-8"), DATA_MIME_TYPES["toml"], "toml"
    elif target_clean == "ndjson":
        if df is None:
            df = _to_dataframe(data_obj)
        ndjson_str = df.to_json(orient="records", lines=True)
        return ndjson_str.encode("utf-8"), DATA_MIME_TYPES["ndjson"], "ndjson"
    elif target_clean == "ini":
        ini_str = _to_ini_str(data_obj)
        return ini_str.encode("utf-8"), DATA_MIME_TYPES["ini"], "ini"
    elif target_clean == "parquet":
        if df is None:
            df = _to_dataframe(data_obj)
        out_buf = io.BytesIO()
        df.to_parquet(out_buf, index=False)
        return out_buf.getvalue(), DATA_MIME_TYPES["parquet"], "parquet"
    elif target_clean == "json":
        out_str = json.dumps(data_obj, indent=2, ensure_ascii=False)
        return out_str.encode("utf-8"), DATA_MIME_TYPES["json"], "json"
    elif target_clean == "yaml":
        out_str = yaml.safe_dump(data_obj, sort_keys=False)
        return out_str.encode("utf-8"), DATA_MIME_TYPES["yaml"], "yaml"
    elif target_clean == "csv":
        if df is None:
            df = _to_dataframe(data_obj)
        out_buf = io.StringIO()
        df.to_csv(out_buf, index=False)
        return out_buf.getvalue().encode("utf-8"), DATA_MIME_TYPES["csv"], "csv"
    elif target_clean == "tsv":
        if df is None:
            df = _to_dataframe(data_obj)
        out_buf = io.StringIO()
        df.to_csv(out_buf, sep="\t", index=False)
        return out_buf.getvalue().encode("utf-8"), DATA_MIME_TYPES["tsv"], "tsv"
    elif target_clean == "sql":
        if df is None:
            df = _to_dataframe(data_obj)
        sql_str = _generate_sql_inserts(df, table_name)
        return sql_str.encode("utf-8"), DATA_MIME_TYPES["sql"], "sql"
    elif target_clean == "xml":
        xml_bytes = _to_xml_bytes(data_obj)
        return xml_bytes, DATA_MIME_TYPES["xml"], "xml"

    out_str = json.dumps(data_obj, indent=2)
    return out_str.encode("utf-8"), DATA_MIME_TYPES["json"], "json"


# --- Helper Functions ---

def _parse_input_data(input_bytes: bytes, src_clean: str) -> Tuple[Union[Dict, List], Any]:
    """Parses payload into Python object and DataFrame."""
    if src_clean == "plist":
        try:
            obj = plistlib.loads(input_bytes)
            return obj, _to_dataframe(obj)
        except Exception as e:
            raise ValueError(f"Failed to parse Apple PLIST payload: {e}")

    if src_clean == "parquet":
        try:
            df = pd.read_parquet(io.BytesIO(input_bytes))
            obj = df.to_dict(orient="records")
            return obj, df
        except Exception as e:
            raise ValueError(f"Failed to parse Parquet payload: {e}")

    raw_text = input_bytes.decode("utf-8", errors="ignore").strip()

    if src_clean == "vcf":
        # Parse vCard contacts
        records = []
        current = {}
        for line in raw_text.splitlines():
            if line.startswith("BEGIN:VCARD"):
                current = {}
            elif line.startswith("END:VCARD"):
                if current:
                    records.append(current)
            elif ":" in line:
                key, val = line.split(":", 1)
                clean_key = key.split(";")[0].lower()
                current[clean_key] = val.strip()
        df = pd.DataFrame(records if records else [{"contact": raw_text}])
        return records, df
    elif src_clean == "ndjson":
        records = [json.loads(line) for line in raw_text.splitlines() if line.strip()]
        df = pd.DataFrame(records)
        return records, df
    elif src_clean == "ini":
        config = configparser.ConfigParser()
        config.read_string(raw_text)
        obj = {section: dict(config[section]) for section in config.sections()}
        df = pd.DataFrame(obj)
        return obj, df
    elif src_clean == "json":
        obj = json.loads(raw_text)
        df = _to_dataframe(obj)
        return obj, df
    elif src_clean == "yaml":
        obj = yaml.safe_load(raw_text)
        df = _to_dataframe(obj)
        return obj, df
    elif src_clean in ["csv", "tsv"]:
        sep = "\t" if src_clean == "tsv" else ","
        df = pd.read_csv(io.StringIO(raw_text), sep=sep)
        obj = df.to_dict(orient="records")
        return obj, df
    elif src_clean == "xml":
        root = ET.fromstring(raw_text)
        records = []
        for child in root:
            row = {sub.tag: sub.text for sub in child}
            if row:
                records.append(row)
        if not records:
            records = [{root.tag: root.text}]
        df = pd.DataFrame(records)
        return records, df
    else:
        try:
            obj = json.loads(raw_text)
            return obj, _to_dataframe(obj)
        except Exception:
            return {"raw_content": raw_text}, pd.DataFrame([{"raw_content": raw_text}])


def _to_dataframe(data_obj: Union[Dict, List]) -> pd.DataFrame:
    """Safely converts dict or list to pandas DataFrame."""
    if isinstance(data_obj, list):
        return pd.DataFrame(data_obj)
    elif isinstance(data_obj, dict):
        return pd.DataFrame([data_obj])
    return pd.DataFrame([{"value": str(data_obj)}])


def _to_plist_bytes(data_obj: Union[Dict, List]) -> bytes:
    """Serializes Python object to Apple XML Property List bytes."""
    if not isinstance(data_obj, (dict, list)):
        data_obj = {"value": str(data_obj)}
    return plistlib.dumps(data_obj, fmt=plistlib.FMT_XML)


def _to_vcard_str(df: pd.DataFrame) -> str:
    """Generates vCard .vcf string from DataFrame records."""
    vcards = []
    for _, row in df.iterrows():
        fn = str(row.get("fn", row.get("name", "Contact"))).strip()
        email = str(row.get("email", "")).strip()
        tel = str(row.get("tel", row.get("phone", ""))).strip()

        lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{fn}"]
        if email:
            lines.append(f"EMAIL:{email}")
        if tel:
            lines.append(f"TEL:{tel}")
        lines.append("END:VCARD")
        vcards.append("\n".join(lines))

    return "\n\n".join(vcards)


def _to_toml_str(data_obj: Union[Dict, List]) -> str:
    """Simple TOML serializer fallback."""
    lines = []
    if isinstance(data_obj, dict):
        for k, v in data_obj.items():
            if isinstance(v, (int, float, bool)):
                lines.append(f"{k} = {str(v).lower()}")
            else:
                lines.append(f'{k} = "{v}"')
    elif isinstance(data_obj, list):
        for i, item in enumerate(data_obj):
            lines.append(f"[[item]]")
            if isinstance(item, dict):
                for k, v in item.items():
                    lines.append(f'{k} = "{v}"')
    return "\n".join(lines) if lines else "title = 'OmniConvert Export'"


def _to_ini_str(data_obj: Union[Dict, List]) -> str:
    """INI format serializer."""
    config = configparser.ConfigParser()
    if isinstance(data_obj, dict):
        for k, v in data_obj.items():
            if isinstance(v, dict):
                config[str(k)] = {str(sub_k): str(sub_v) for sub_k, sub_v in v.items()}
            else:
                config["DEFAULT"] = {str(k): str(v)}
    out = io.StringIO()
    config.write(out)
    return out.getvalue()


def _generate_sql_inserts(df: pd.DataFrame, table_name: str) -> str:
    """Generates SQL INSERT INTO statements from a DataFrame."""
    lines = [f"-- SQL Export generated for table '{table_name}'", ""]
    columns = list(df.columns)
    cols_str = ", ".join(f"`{c}`" for c in columns)

    for _, row in df.iterrows():
        vals = []
        for val in row:
            if pd.isna(val):
                vals.append("NULL")
            elif isinstance(val, (int, float)):
                vals.append(str(val))
            elif isinstance(val, bool):
                vals.append("TRUE" if val else "FALSE")
            else:
                escaped = str(val).replace("'", "''")
                vals.append(f"'{escaped}'")
        vals_str = ", ".join(vals)
        lines.append(f"INSERT INTO `{table_name}` ({cols_str}) VALUES ({vals_str});")

    return "\n".join(lines)


def _to_xml_bytes(data_obj: Union[Dict, List]) -> bytes:
    """Converts a dict or list of dicts to XML bytes."""
    root = ET.Element("root")

    if isinstance(data_obj, list):
        for item in data_obj:
            item_elem = ET.SubElement(root, "item")
            if isinstance(item, dict):
                for k, v in item.items():
                    sub = ET.SubElement(item_elem, str(k))
                    sub.text = str(v) if v is not None else ""
            else:
                item_elem.text = str(item)
    elif isinstance(data_obj, dict):
        for k, v in data_obj.items():
            sub = ET.SubElement(root, str(k))
            sub.text = str(v) if v is not None else ""
    else:
        root.text = str(data_obj)

    tree = ET.ElementTree(root)
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()
