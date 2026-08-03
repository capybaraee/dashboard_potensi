from __future__ import annotations

import pandas as pd
import streamlit as st

from data_loader import load_sirup_data
from metrics import (
    am_summary,
    cbase_operational_summary,
    cbase_status_summary,
    portfolio_summary,
    pending_potential,
    satker_operational_summary,
    summary_metrics,
)
from ui import (
    format_integer,
    format_rupiah,
    inject_css,
    render_am_accordion_table,
    render_cbase_accordion_table,
    render_info_pills,
    render_metric_cards,
    render_page_header,
    render_portfolio_card,
    render_progress,
    render_section_header,
    render_total_bar,
)

st.set_page_config(
    page_title="Dashboard Potensi SIRUP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


def _portfolio_options(df: pd.DataFrame) -> list[str]:
    order = ["Network", "Device", "Application", "Service", "Media"]
    available = set(df["PORTOFOLIO"].dropna().astype(str).tolist())
    ordered = [name for name in order if name in available]
    ordered.extend(sorted(available.difference(ordered)))
    return ["Semua Portofolio", *ordered]


def _filter_portfolio(df: pd.DataFrame, selected: str) -> pd.DataFrame:
    if selected == "Semua Portofolio":
        return df
    return df[df["PORTOFOLIO"] == selected].copy()


def _portfolio_pills(label: str, options: list[str], key: str) -> str:
    if hasattr(st, "pills"):
        selected = st.pills(
            label,
            options,
            default=options[0],
            selection_mode="single",
            key=key,
            label_visibility="collapsed",
        )
    else:
        selected = st.segmented_control(
            label,
            options,
            default=options[0],
            key=key,
            label_visibility="collapsed",
        )
    return str(selected or options[0])


def _render_overview(data: pd.DataFrame) -> None:
    render_page_header(
        "Overview Potensi SIRUP",
        "Semua Account Manager dan Government Customer · Total Pagu = Belum + Sudah Pengadaan",
    )

    overall = summary_metrics(data)
    render_metric_cards(overall)
    render_progress(overall)

    render_section_header(
        "Breakdown per Portofolio",
        "Diurutkan berdasarkan nilai PAGU belum pengadaan terbesar.",
    )
    portfolio = portfolio_summary(data)
    if portfolio.empty:
        st.info("Belum ada data portofolio.")
    else:
        columns = st.columns(3)
        for index, (_, row) in enumerate(portfolio.iterrows()):
            with columns[index % 3]:
                render_portfolio_card(row)

    st.divider()
    render_section_header(
        "Ringkasan per Account Manager",
        "Klik baris AM untuk membuka seluruh Government Customer/CBASE yang ditangani.",
    )
    options = _portfolio_options(data)
    selected = _portfolio_pills("Filter Portofolio", options, "overview_portfolio")
    filtered = _filter_portfolio(data, selected)
    am_table = am_summary(filtered)

    if am_table.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return

    cbase_tables: dict[str, pd.DataFrame] = {}
    for am_name in am_table["AM"].astype(str):
        am_data = filtered[filtered["AM"] == am_name]
        cbase_tables[am_name] = cbase_status_summary(am_data)

    render_am_accordion_table(am_table, cbase_tables)

    filtered_metrics = summary_metrics(filtered)
    render_total_bar(
        "GRAND TOTAL SEMUA AM",
        package_count=int(filtered_metrics["paket_total"]),
        total_pagu=int(filtered_metrics["total"]),
        satker_count=int(filtered_metrics["satker"]),
    )


def _render_am_page(data: pd.DataFrame, am_name: str) -> None:
    am_data = data[data["AM"] == am_name].copy()
    if am_data.empty:
        st.warning("Data AM tidak ditemukan.")
        return

    territories = (
        am_data[["CBASE_KEY", "CBASE"]]
        .drop_duplicates("CBASE_KEY")["CBASE"]
        .sort_values()
        .tolist()
    )
    render_page_header(am_name, " · ".join(territories))

    am_metrics = summary_metrics(am_data)
    render_metric_cards(am_metrics)
    render_progress(am_metrics)
    render_info_pills(am_metrics)

    render_section_header(
        "Potensi SIRUP per CBASE",
        "Klik CBASE untuk membuka daftar SATKER. Klik nama SATKER untuk melihat detail paket.",
    )
    options = _portfolio_options(am_data)
    selected = _portfolio_pills("Filter Portofolio", options, f"am_portfolio_{am_name}")

    # Card dan progress tetap memakai seluruh paket (Belum + Sudah).
    # Tabel operasional hanya menampilkan paket yang masih Belum Pengadaan.
    filtered_all = _filter_portfolio(am_data, selected)
    potential_data = pending_potential(filtered_all)
    cbase_table = cbase_operational_summary(potential_data)

    if cbase_table.empty:
        st.success(
            "Tidak ada paket Belum Pengadaan pada portofolio ini. "
            "Seluruh paket yang tersedia sudah berstatus Sudah Ada Pengadaan."
        )
    else:
        satker_tables: dict[str, pd.DataFrame] = {}
        satker_detail_tables: dict[tuple[str, str], pd.DataFrame] = {}

        for _, cbase_row in cbase_table.iterrows():
            cbase_key = str(cbase_row["CBASE_KEY"])
            cbase_data = potential_data[
                potential_data["CBASE_KEY"] == cbase_key
            ].copy()
            satker_tables[cbase_key] = satker_operational_summary(cbase_data)

            for satker_name, satker_data in cbase_data.groupby(
                "SATKER",
                dropna=False,
            ):
                satker_detail_tables[(cbase_key, str(satker_name))] = (
                    satker_data.copy()
                )

        render_cbase_accordion_table(
            cbase_table,
            satker_tables,
            am_name,
            satker_detail_tables,
        )

        potential_metrics = summary_metrics(potential_data)
        render_total_bar(
            "TOTAL POTENSI BELUM PENGADAAN",
            package_count=int(potential_metrics["paket_total"]),
            total_pagu=int(potential_metrics["total"]),
            satker_count=int(potential_metrics["satker"]),
        )



try:
    data, metadata = load_sirup_data()
except Exception as error:
    st.error("Data Google Sheets belum dapat dibaca.")
    st.exception(error)
    st.info(
        "Pastikan spreadsheet dapat dibaca oleh aplikasi, worksheet bernama SIRUP0726, dan secrets.toml sudah benar."
    )
    st.stop()

if data.empty:
    st.warning("Worksheet SIRUP0726 tidak memiliki data aktif.")
    st.stop()

am_table_sidebar = am_summary(data)
valid_ams = am_table_sidebar[am_table_sidebar["AM"] != "UNMAPPED"].copy()
valid_am_names = set(valid_ams["AM"].astype(str))

if "active_page" not in st.session_state:
    st.session_state.active_page = "OVERVIEW"

query_page = str(st.query_params.get("page", ""))
if query_page in valid_am_names:
    st.session_state.active_page = query_page

with st.sidebar:
    st.markdown("### Dashboard Potensi")
    st.caption("Witel Riau & Kepri · SIRUP0726")
    st.divider()

    overview_type = "primary" if st.session_state.active_page == "OVERVIEW" else "secondary"
    if st.button("Overview Semua AM", use_container_width=True, type=overview_type):
        st.query_params.clear()
        st.session_state.active_page = "OVERVIEW"
        st.rerun()

    st.markdown("#### Account Manager")
    for _, row in valid_ams.iterrows():
        am_name = str(row["AM"])
        pct = float(row["PROGRESS"]) * 100
        label = f"{am_name}  ·  {pct:.0f}%"
        button_type = "primary" if st.session_state.active_page == am_name else "secondary"

        if st.button(
            label,
            key=f"nav_{am_name}",
            use_container_width=True,
            type=button_type,
        ):
            st.query_params.clear()
            st.session_state.active_page = am_name
            st.rerun()

    st.divider()
    if st.button("↻  Perbarui Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    loaded = metadata["loaded_at"]
    st.caption(f"Dibaca: {loaded:%d %b %Y · %H:%M}")
    if metadata["unmapped_rows"]:
        st.warning(f"{metadata['unmapped_rows']} baris masih UNMAPPED.")
    if metadata["excluded_status_rows"]:
        st.caption(
            f"{metadata['excluded_status_rows']} baris status lain/Take Out tidak dihitung."
        )

active_page = st.session_state.active_page
if active_page == "OVERVIEW":
    _render_overview(data)
else:
    _render_am_page(data, active_page)
