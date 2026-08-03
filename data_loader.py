from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any
from urllib.parse import quote

import pandas as pd
import streamlit as st


SPREADSHEET_ID = st.secrets["google_sheets"]["spreadsheet_id"]
SIRUP_SHEET = st.secrets["google_sheets"].get(
    "sirup_sheet",
    "SIRUP0726",
)
SIRUP_GID = str(st.secrets["google_sheets"]["sirup_gid"])

MAPPING_SHEET = st.secrets["google_sheets"].get(
    "mapping_sheet",
    "MAPPING AM 2026",
)

VALID_STATUSES = ("Belum Pengadaan", "Sudah Ada Pengadaan")


def _sheet_csv_url(sheet_name: str) -> str:
    if sheet_name == SIRUP_SHEET:
        return (
            f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export"
            f"?format=csv&gid={SIRUP_GID}"
        )

    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(sheet_name)}"
    )


def _make_unique(headers: list[Any]) -> list[str]:
    counts: dict[str, int] = {}
    result: list[str] = []
    for value in headers:
        name = str(value).strip() if value is not None else ""
        name = name or "UNNAMED"
        counts[name] = counts.get(name, 0) + 1
        result.append(name if counts[name] == 1 else f"{name}__{counts[name]}")
    return result


def _read_public_sheet(sheet_name: str, header_marker: str) -> pd.DataFrame:
    """Read a public Google Sheet and detect its actual header row."""
    raw = pd.read_csv(
        _sheet_csv_url(sheet_name),
        header=None,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )

    marker = header_marker.strip().upper()
    header_index: int | None = None
    for index, row in raw.iterrows():
        values = row.astype(str).str.strip().str.upper()
        if marker in set(values.tolist()):
            header_index = int(index)
            break

    if header_index is None:
        raise ValueError(
            f"Header '{header_marker}' tidak ditemukan pada worksheet {sheet_name}."
        )

    headers = _make_unique(raw.iloc[header_index].tolist())
    data = raw.iloc[header_index + 1 :].copy()
    data.columns = headers
    data = data.reset_index(drop=True)
    data = data.replace({"": pd.NA})
    data = data.dropna(how="all")
    return data


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str:
    normalized = {str(column).strip().upper(): column for column in df.columns}
    for candidate in candidates:
        candidate_upper = candidate.strip().upper()
        if candidate_upper in normalized:
            return str(normalized[candidate_upper])

    # Fallback: startswith match for duplicated headers such as Portofolio__2.
    for candidate in candidates:
        candidate_upper = candidate.strip().upper()
        for column in df.columns:
            if str(column).strip().upper().startswith(candidate_upper):
                return str(column)

    raise KeyError(f"Kolom tidak ditemukan. Kandidat: {', '.join(candidates)}")


def _text(series: pd.Series) -> pd.Series:
    return (
        series.fillna("")
        .astype(str)
        .str.replace("\u00a0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def _key_text(series: pd.Series) -> pd.Series:
    return _text(series).str.upper()


def _parse_money(value: Any) -> int:
    if value is None or pd.isna(value):
        return 0

    text = str(value).strip()
    if not text or text in {"-", "—", "nan", "None"}:
        return 0

    cleaned = re.sub(r"(?i)rp\s*", "", text).strip()

    # Scientific notation, occasionally produced by exported Excel values.
    if re.fullmatch(r"-?\d+(?:\.\d+)?[eE][+-]?\d+", cleaned):
        try:
            return int(Decimal(cleaned))
        except (InvalidOperation, ValueError):
            return 0

    # Plain decimal produced by CSV export: 6000000000.0
    if re.fullmatch(r"-?\d+\.0+", cleaned):
        try:
            return int(float(cleaned))
        except ValueError:
            return 0

    # Indonesian thousand separators: 6.000.000.000 / 6,000,000,000.
    digits = re.sub(r"[^0-9-]", "", cleaned)
    if not digits or digits == "-":
        return 0
    try:
        return int(digits)
    except ValueError:
        return 0


def _normalize_package_id(value: Any, fallback: str) -> str:
    if value is None or pd.isna(value):
        return fallback
    text = str(value).strip()
    if not text:
        return fallback
    try:
        if re.fullmatch(r"\d+(?:\.0+)?", text):
            return str(int(float(text)))
        if re.fullmatch(r"\d+(?:\.\d+)?[eE][+-]?\d+", text):
            return str(int(Decimal(text)))
    except (ValueError, InvalidOperation):
        pass
    return text


def _clean_satker(value: Any) -> str:
    text = "" if value is None or pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text.replace("\u00a0", " ")).strip()
    # Remove administrative code suffix, for example: " - 2.16.2.20...".
    text = re.sub(r"\s+-\s+\d[\d.]*$", "", text).strip()
    return text or "SATKER tidak tersedia"


def _pretty_cbase(value: Any) -> str:
    text = "" if value is None or pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text.replace("\u00a0", " ")).strip()
    if not text:
        return "CBASE tidak tersedia"
    if text.isupper():
        text = text.title()
    replacements = {
        "Pemkab": "Pemkab",
        "Pemkot": "Pemkot",
        "Pemprov": "Pemprov",
        "Polda": "POLDA",
        "Kpu": "KPU",
        "Dprd": "DPRD",
    }
    for source, target in replacements.items():
        text = re.sub(rf"\b{source}\b", target, text)
    return text


def _normalize_status(value: Any) -> str:
    text = "" if value is None or pd.isna(value) else str(value).strip().upper()
    if "BELUM" in text:
        return "Belum Pengadaan"
    if "SUDAH" in text:
        return "Sudah Ada Pengadaan"
    return "Status Lain"


def _normalize_portfolio(value: Any) -> str:
    text = "" if value is None or pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "Lainnya"
    canonical = {
        "NETWORK": "Network",
        "DEVICE": "Device",
        "APPLICATION": "Application",
        "SERVICE": "Service",
        "MEDIA": "Media",
    }
    return canonical.get(text.upper(), text.title())


def _load_mapping_fallback() -> dict[str, str]:
    """Use the latest re-mapping column only when the SIRUP AM formula is blank."""
    try:
        mapping = _read_public_sheet(MAPPING_SHEET, "GC")
    except Exception:
        return {}

    gc_col = _find_column(mapping, ["GC", "CBASE", "Government Customer"])
    remap_columns = [
        column
        for column in mapping.columns
        if "RE-MAPPING" in str(column).upper() or "MAPPING" in str(column).upper()
    ]
    if not remap_columns:
        return {}

    def quarter_number(column: str) -> int:
        match = re.search(r"Q(\d+)", str(column).upper())
        return int(match.group(1)) if match else 0

    latest_column = sorted(remap_columns, key=quarter_number)[-1]
    result: dict[str, str] = {}
    for _, row in mapping.iterrows():
        gc = str(row.get(gc_col, "") or "").strip().upper()
        am = str(row.get(latest_column, "") or "").strip().upper()
        if gc and am and am not in {"NAN", "NONE"}:
            result[gc] = am
    return result


@st.cache_data(ttl=600, show_spinner="Membaca data SIRUP0726...")
def load_sirup_data() -> tuple[pd.DataFrame, dict[str, Any]]:
    source = _read_public_sheet(SIRUP_SHEET, "ID RUP")

    columns = {
        "id": _find_column(source, ["ID RUP"]),
        "status": _find_column(source, ["Pengadaan"]),
        "cbase": _find_column(source, ["CBASE"]),
        "satker": _find_column(source, ["SATKER"]),
        "package": _find_column(source, ["Nama Paket"]),
        "portfolio": _find_column(source, ["Portofolio"]),
        "pagu": _find_column(source, ["PAGU"]),
        "am": _find_column(source, ["AM"]),
    }

    data = pd.DataFrame(index=source.index)
    data["ID_RUP_RAW"] = source[columns["id"]]
    data["STATUS_PENGADAAN"] = source[columns["status"]].map(_normalize_status)
    data["CBASE_KEY"] = _key_text(source[columns["cbase"]])
    data["CBASE"] = source[columns["cbase"]].map(_pretty_cbase)
    data["SATKER"] = source[columns["satker"]].map(_clean_satker)
    data["NAMA_PAKET"] = _text(source[columns["package"]]).replace("", "Paket tanpa nama")
    data["PORTOFOLIO"] = source[columns["portfolio"]].map(_normalize_portfolio)
    data["PAGU"] = source[columns["pagu"]].map(_parse_money).astype("int64")
    data["AM"] = _key_text(source[columns["am"]])

    # The SIRUP sheet formula is the primary source. Mapping sheet is only a fallback.
    invalid_am = data["AM"].isin(["", "UNMAPPED", "NAN", "NONE"])
    mapping = _load_mapping_fallback()
    if mapping:
        data.loc[invalid_am, "AM"] = data.loc[invalid_am, "CBASE_KEY"].map(mapping).fillna("")

    # Use another valid row from the same CBASE as the second fallback.
    valid_rows = data[~data["AM"].isin(["", "UNMAPPED", "NAN", "NONE"])]
    if not valid_rows.empty:
        mode_mapping = (
            valid_rows.groupby("CBASE_KEY")["AM"]
            .agg(lambda values: values.mode().iat[0] if not values.mode().empty else values.iloc[0])
            .to_dict()
        )
        invalid_am = data["AM"].isin(["", "UNMAPPED", "NAN", "NONE"])
        data.loc[invalid_am, "AM"] = data.loc[invalid_am, "CBASE_KEY"].map(mode_mapping).fillna("")

    data["AM"] = data["AM"].replace("", "UNMAPPED")
    data["PACKAGE_KEY"] = [
        _normalize_package_id(value, f"ROW-{index}")
        for index, value in enumerate(data["ID_RUP_RAW"], start=1)
    ]

    raw_count = len(data)
    excluded_status_count = int((~data["STATUS_PENGADAAN"].isin(VALID_STATUSES)).sum())
    unmapped_count = int((data["AM"] == "UNMAPPED").sum())

    # Total Pagu must be exactly Belum + Sudah, so Take Out/status lain is excluded.
    data = data[data["STATUS_PENGADAAN"].isin(VALID_STATUSES)].copy()
    data = data[data["CBASE_KEY"].ne("")].copy()
    data = data.reset_index(drop=True)

    loaded_at = datetime.now().astimezone()
    metadata = {
        "loaded_at": loaded_at,
        "raw_rows": raw_count,
        "active_rows": len(data),
        "excluded_status_rows": excluded_status_count,
        "unmapped_rows": unmapped_count,
        "source_url": f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit",
    }
    return data, metadata