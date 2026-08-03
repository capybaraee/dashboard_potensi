from __future__ import annotations

import hashlib
import re
from html import escape
from typing import Mapping

import pandas as pd
import streamlit as st


CSS = r"""
<style>
:root {
  --pot-bg: #f4f6fb;
  --pot-card: #ffffff;
  --pot-border: #dce3ec;
  --pot-border-soft: #e8edf3;
  --pot-text: #0f172a;
  --pot-body: #334155;
  --pot-muted: #64748b;
  --pot-blue: #2563eb;
  --pot-blue-dark: #1e3a8a;
  --pot-blue-soft: #eff6ff;
  --pot-teal: #0f766e;
  --pot-orange: #ea6a2a;
  --pot-orange-dark: #b94719;
  --pot-orange-soft: #fff1e9;
  --pot-green: #159a52;
  --pot-green-soft: #eaf8f0;
  --pot-red: #d83a3a;
  --pot-red-soft: #ffeded;
  --pot-shadow: 0 7px 20px rgba(15, 23, 42, .045);
  --drawer-offset-top: 48px;
}

html, body, [class*="css"] { font-family: "Inter", "Segoe UI", sans-serif; }
.stApp { background: var(--pot-bg); }
.block-container { max-width: 1540px; padding-top: 1rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--pot-border); }
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

.pot-title { color: var(--pot-text); font-size: 1.42rem; line-height: 1.2; font-weight: 850; }
.pot-subtitle { margin-top: .22rem; color: var(--pot-muted); font-size: .76rem; }
.pot-section-title { margin: .16rem 0 .16rem; color: var(--pot-text); font-size: 1rem; font-weight: 850; }
.pot-section-sub { margin-bottom: .68rem; color: var(--pot-muted); font-size: .74rem; }

.metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .78rem; margin: .9rem 0 .85rem; }
.metric-card { position: relative; overflow: hidden; padding: .92rem 1rem; background: #fff; border: 1px solid var(--pot-border); border-radius: 14px; box-shadow: 0 3px 12px rgba(15,23,42,.035); }
.metric-card::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 4px; background: var(--pot-blue); }
.metric-card.belum { background: linear-gradient(180deg,#fff,#fff8f4); border-color: #ffd5c0; }
.metric-card.belum::after { background: var(--pot-orange); }
.metric-card.sudah { background: linear-gradient(180deg,#fff,#f7fff9); }
.metric-card.sudah::after { background: var(--pot-green); }
.metric-label { color: var(--pot-muted); font-size: .64rem; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; }
.metric-value { margin-top: .3rem; color: var(--pot-text); font-size: 1.5rem; font-weight: 850; }
.metric-card.belum .metric-value { color: var(--pot-orange-dark); }
.metric-card.sudah .metric-value { color: #147d45; }
.metric-meta { margin-top: .24rem; color: var(--pot-muted); font-size: .68rem; }
.metric-callout { display: inline-block; margin-top: .4rem; padding: .18rem .45rem; border-radius: 999px; background: var(--pot-orange-soft); color: var(--pot-orange-dark); font-size: .63rem; font-weight: 750; }

.progress-wrap { padding: .82rem 1rem; margin-bottom: 1.05rem; background: #fff; border: 1px solid var(--pot-border); border-radius: 14px; box-shadow: 0 3px 12px rgba(15,23,42,.03); }
.progress-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.progress-title { color: var(--pot-text); font-size: .76rem; font-weight: 800; }
.progress-pct { color: var(--pot-green); font-size: .84rem; font-weight: 850; }
.progress-track { height: 10px; overflow: hidden; margin: .56rem 0 .42rem; background: #ffe4d8; border-radius: 999px; }
.progress-fill { height: 100%; background: linear-gradient(90deg,#11894a,#27b568); border-radius: 999px; }
.progress-legend { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .4rem 1rem; color: var(--pot-muted); font-size: .67rem; }
.progress-legend strong { color: var(--pot-text); }

.portfolio-card { min-height: 136px; margin: .22rem 0 .72rem; padding: .9rem .88rem; background: #fff; border: 1px solid var(--pot-border); border-radius: 13px; box-shadow: 0 4px 14px rgba(15,23,42,.03); }
.portfolio-name { margin-bottom: .5rem; color: var(--pot-text); font-size: .8rem; font-weight: 850; }
.portfolio-row { display: flex; justify-content: space-between; gap: .8rem; padding: .16rem 0; color: var(--pot-muted); font-size: .69rem; }
.portfolio-row strong { color: var(--pot-text); font-variant-numeric: tabular-nums; }
.portfolio-row.belum strong { color: var(--pot-orange-dark); }
.portfolio-mini-track { height: 6px; margin-top: .5rem; overflow: hidden; background: #ffe3d6; border-radius: 999px; }
.portfolio-mini-fill { height: 100%; background: var(--pot-green); border-radius: 999px; }
.portfolio-progress { margin-top: .28rem; color: var(--pot-muted); font-size: .65rem; }

.info-strip { display: flex; flex-wrap: wrap; gap: .4rem; margin: .58rem 0 .9rem; }
.info-pill { display: inline-flex; align-items: center; gap: .28rem; padding: .31rem .62rem; background: #fff; border: 1px solid var(--pot-border); border-radius: 999px; color: var(--pot-muted); font-size: .68rem; }
.info-pill strong { color: var(--pot-text); }
.info-pill.alert { background: var(--pot-orange-soft); border-color: #ffd4c0; color: var(--pot-orange-dark); }
.info-pill.alert strong { color: var(--pot-orange-dark); }

.total-bar { display: grid; grid-template-columns: minmax(0,1fr) auto auto; gap: 1rem; align-items: center; margin-top: .42rem; padding: .62rem .78rem; background: #eef3fb; border: 1px solid #d7e0ed; border-top: 2px solid #b9c8dd; border-radius: 9px; color: var(--pot-text); font-size: .72rem; font-weight: 850; }
.total-bar .muted { color: var(--pot-muted); font-weight: 650; }

/* Filter pills */
div[data-testid="stPills"] { margin-bottom: .3rem; }
div[data-testid="stPills"] button {
  min-height: 32px !important;
  padding: 0 12px !important;
  background: #fff !important;
  border: 1px solid #d7dfeb !important;
  border-radius: 999px !important;
  color: #43506a !important;
  box-shadow: 0 2px 7px rgba(24,39,75,.035) !important;
  font-size: .71rem !important;
  font-weight: 750 !important;
}
div[data-testid="stPills"] button:hover { background: #f6f9ff !important; border-color: #9db6ea !important; color: var(--pot-blue) !important; }
div[data-testid="stPills"] button[aria-pressed="true"] { background: linear-gradient(90deg,var(--pot-blue-dark),var(--pot-blue)) !important; border-color: transparent !important; color: #fff !important; box-shadow: 0 6px 16px rgba(32,85,214,.18) !important; }

/* Sidebar AM buttons: percentage stays in the same button label. */
[data-testid="stSidebar"] .stButton > button {
  justify-content: flex-start !important;
  min-height: 37px !important;
  padding: 0 .72rem !important;
  border-radius: 9px !important;
  font-size: .69rem !important;
  font-weight: 760 !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] { background: #fff !important; border: 1px solid #d8deea !important; color: #26344f !important; }
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover { background: #f4f7fc !important; border-color: #aec0e4 !important; }
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] { background: linear-gradient(90deg,var(--pot-blue-dark),var(--pot-blue)) !important; border: 1px solid transparent !important; color: #fff !important; }

/* =====================================================
   HIERARCHY TABLE — adapted from Overview Sales per AM
   ===================================================== */
.accordion-shell { overflow-x: auto; background: #fff; border: 1px solid #dce3ec; border-radius: 12px; box-shadow: var(--pot-shadow); }
.accordion-inner { min-width: 980px; color: var(--pot-body); font-size: .62rem; font-variant-numeric: tabular-nums; }
.accordion-head,
.accordion-summary,
.accordion-row { display: grid; align-items: stretch; }
.am-grid { grid-template-columns: minmax(240px,2.45fr) 96px 142px 158px 158px 112px; }
.cbase-grid { grid-template-columns: minmax(330px,2.85fr) 102px 102px 158px; }

.accordion-head { background: #1e3a8a; color: #fff; font-size: .6rem; font-weight: 800; letter-spacing: .02em; text-transform: uppercase; }
.accordion-head.overview { background: linear-gradient(90deg,#1e3a8a,#1d4ed8 62%,#0f766e); }
.accordion-head.operational { background: linear-gradient(90deg,#0f635c,#0f766e,#168b80); }
.accordion-head > div,
.accordion-summary > div,
.accordion-row > div {
  display: flex;
  align-items: center;
  min-width: 0;
  min-height: 35px;
  padding: .34rem .42rem;
  box-sizing: border-box;
  border-right: 1px solid #e5eaf1;
}
.accordion-head > div { justify-content: flex-start; border-right-color: rgba(255,255,255,.2); }
.accordion-head > div:last-child,
.accordion-summary > div:last-child,
.accordion-row > div:last-child { border-right: 0; }
.accordion-head .num,
.accordion-summary .num,
.accordion-row .num { justify-content: flex-end; text-align: right; }

.pot-accordion { margin: 0; background: #fff; border-top: 1px solid #e5eaf1; }
.pot-accordion:first-of-type { border-top: 0; }
.pot-accordion > summary { list-style: none; cursor: pointer; }
.pot-accordion > summary::-webkit-details-marker { display: none; }
.accordion-summary { background: #fff; color: #0f172a; font-size: .62rem; font-weight: 800; }
.accordion-summary:hover { background: #f4f8ff; }
.pot-accordion[open] > .accordion-summary { background: #eff6ff; border-bottom: 1px solid #dbe5f2; }

.cell-label { display: flex; align-items: center; gap: .38rem; min-width: 0; }
.cell-label .label-text { overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.chevron { display: inline-flex; align-items: center; justify-content: center; width: 13px; height: 13px; flex: 0 0 13px; color: var(--pot-blue); font-size: .68rem; }
.chevron::before { content: "▸"; }
.pot-accordion[open] .chevron::before { content: "▾"; }
.cbase-count-text { margin-left: .2rem; color: var(--pot-muted); font-size: .56rem; font-weight: 700; white-space: nowrap; }

/* Expanded area is visibly grey and uses exactly the same font size. */
.accordion-body-flat { padding: 0; background: #f8fafc; border-top: 0; }
.accordion-body-flat .accordion-row { background: #f8fafc; color: #334155; font-size: .62rem; font-weight: 650; border-top: 1px solid #e8edf3; }
.accordion-body-flat .accordion-row:first-child { border-top: 0; }
.accordion-body-flat .accordion-row:nth-child(even) { background: #f4f6f9; }
.accordion-body-flat .accordion-row:hover { background: #eef3f8; }
.child-name-cell { position: relative; padding-left: 1.55rem !important; color: #334155; font-size: .62rem !important; font-weight: 700; }
.child-name-cell::before { content: "↳"; position: absolute; left: .72rem; color: #64748b; font-size: .62rem; }
.child-empty { justify-content: center !important; color: #c1c9d4; }
.satker-link { color: #334155; font-size: .62rem; font-weight: 700; text-decoration: none; border: 0; }
.satker-link:hover { color: var(--pot-blue); text-decoration: underline; }
.row-sub { display: none; }

.highlight-belum { background: #fff0e8; color: var(--pot-orange-dark); font-weight: 850; }
.highlight-sudah { color: #147d45; font-weight: 800; }
.progress-chip { display: inline-flex; align-items: center; justify-content: center; min-width: 54px; padding: .18rem .38rem; border-radius: 999px; font-size: .57rem; font-weight: 850; }
.progress-chip.high { background: var(--pot-green-soft); color: #147d45; }
.progress-chip.mid { background: #fff6d8; color: #9b6800; }
.progress-chip.low { background: var(--pot-red-soft); color: #b72d2d; }

/* =====================================================
   INSTANT RIGHT DRAWER — pre-rendered and opened with :target
   ===================================================== */
.instant-drawer {
  position: fixed;
  inset: 0;
  z-index: 99979;
  visibility: hidden;
  opacity: 0;
  pointer-events: none;
  transition: opacity .12s ease, visibility .12s ease;
}
.instant-drawer:target {
  visibility: visible;
  opacity: 1;
  pointer-events: auto;
}
.instant-drawer .drawer-overlay {
  position: fixed !important;
  top: var(--drawer-offset-top) !important;
  right: min(720px,46vw) !important;
  bottom: 0 !important;
  left: 0 !important;
  z-index: 99980 !important;
  background: transparent !important;
  text-decoration: none;
}
.instant-drawer .satker-drawer {
  position: fixed !important;
  top: var(--drawer-offset-top) !important;
  right: 0 !important;
  z-index: 99990 !important;
  width: min(720px,46vw) !important;
  min-width: 500px !important;
  height: calc(100vh - var(--drawer-offset-top)) !important;
  overflow-y: auto !important;
  background: #fff !important;
  border-left: 1px solid #d7deea !important;
  border-top: 1px solid #d7deea !important;
  border-top-left-radius: 14px !important;
  box-shadow: -18px 0 42px rgba(20,35,65,.18) !important;
  transform: translateX(100%);
}
.instant-drawer:target .satker-drawer {
  animation: drawerIn .2s cubic-bezier(.22,.8,.32,1) forwards !important;
}
@keyframes drawerIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
.satker-row-anchor { scroll-margin-top: 5rem; }
.drawer-filter-shell { min-height: 100%; }
.drawer-filter-radio { position: absolute; opacity: 0; pointer-events: none; }
.drawer-top { position: sticky; top: 0; z-index: 8; padding: .58rem .95rem .58rem; background: linear-gradient(180deg,#fff 90%,rgba(255,255,255,.96)); border-bottom: 1px solid var(--pot-border); }
.drawer-actions { display: flex; align-items: center; justify-content: space-between; gap: .55rem; margin-bottom: .5rem; }
.drawer-back { display: inline-flex; align-items: center; min-height: 28px; padding: 0 .64rem; background: #fff; border: 1px solid #d8e0ec; border-radius: 999px; color: #334766; text-decoration: none; font-size: .63rem; font-weight: 800; }
.drawer-back:hover { background: #f5f8ff; border-color: #9eb4e3; color: var(--pot-blue); }
.drawer-close { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #fff; border: 1px solid #dce3ee; border-radius: 50%; color: #56627a; text-decoration: none; font-size: 1rem; font-weight: 700; }
.drawer-heading { margin: 0 0 .12rem; color: var(--pot-text); font-size: 1.02rem; font-weight: 850; }
.drawer-sub { color: var(--pot-muted); font-size: .68rem; }
.drawer-filter-label { margin-top: .6rem; margin-bottom: .34rem; color: #4c5870; font-size: .63rem; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }
.drawer-chips { display: flex; flex-wrap: wrap; gap: .34rem; }
.drawer-chip-label { display: inline-flex; align-items: center; min-height: 28px; padding: 0 .58rem; background: #fff; border: 1px solid #d9e1ed; border-radius: 999px; color: #4a5670; cursor: pointer; font-size: .62rem; font-weight: 760; user-select: none; }
.drawer-chip-label:hover { background: #f5f8ff; border-color: #a8bce7; color: var(--pot-blue); }
.drawer-panels { padding: .72rem .92rem 1rem; }
.drawer-panel { display: none; }
.drawer-summary { display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; margin-bottom: .58rem; }
.drawer-mini-card { padding: .62rem .72rem; background: #fff; border: 1px solid var(--pot-border); border-radius: 10px; }
.drawer-mini-label { color: var(--pot-muted); font-size: .58rem; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; }
.drawer-mini-value { margin-top: .2rem; color: var(--pot-text); font-size: 1rem; font-weight: 850; }
.drawer-table { overflow: hidden; background: #fff; border: 1px solid #dce3ed; border-radius: 10px; }
.drawer-table-head,
.drawer-table-row,
.drawer-table-total { display: grid; grid-template-columns: minmax(240px,1fr) 100px 112px; align-items: stretch; }
.drawer-table-head { background: #eaf2ff; color: #1e3a8a; font-size: .57rem; font-weight: 850; letter-spacing: .03em; text-transform: uppercase; }
.drawer-table-row { color: #334155; font-size: .64rem; border-top: 1px solid #e7ecf3; }
.drawer-table-row:nth-child(odd) { background: #fbfcff; }
.drawer-table-row:hover { background: #f1f5f9; }
.drawer-table-head > div,
.drawer-table-row > div,
.drawer-table-total > div { display: flex; align-items: center; min-width: 0; padding: .52rem .58rem; border-right: 1px solid #e0e6ef; }
.drawer-table-head > div:last-child,
.drawer-table-row > div:last-child,
.drawer-table-total > div:last-child { justify-content: flex-end; border-right: 0; text-align: right; }
.drawer-table-total { background: #eaf0f8; border-top: 2px solid #cbd7e7; color: #1d2e49; font-size: .66rem; font-weight: 850; }
.package-name { line-height: 1.32; }
.portfolio-badge { display: inline-flex; align-items: center; justify-content: center; padding: .18rem .4rem; border-radius: 999px; font-size: .56rem; font-weight: 800; white-space: nowrap; }
.portfolio-badge.network { background: #e8f0ff; color: #2457bf; }
.portfolio-badge.device { background: #fff5cc; color: #8b6700; }
.portfolio-badge.application { background: #f0eaff; color: #6940a5; }
.portfolio-badge.service { background: #edf1f5; color: #536174; }
.portfolio-badge.media { background: #e9f8f5; color: #0d756b; }
.portfolio-badge.other { background: #f2f3f6; color: #626b78; }
.drawer-empty { padding: 1rem; color: var(--pot-muted); text-align: center; font-size: .7rem; }


@media (max-width: 1000px) {
  :root { --drawer-offset-top: 0px; }
  .instant-drawer .satker-drawer { width: 100vw !important; min-width: 0 !important; height: 100vh !important; border-top-left-radius: 0 !important; }
  .instant-drawer .drawer-overlay { right: 0 !important; }
}

@media (max-width: 1000px) {
  .metric-grid { grid-template-columns: 1fr; }
  .total-bar { grid-template-columns: 1fr; gap: .22rem; }
  .satker-drawer { width: 100vw !important; max-width: 100vw !important; min-width: 0 !important; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def format_rupiah(value: float | int) -> str:
    amount = float(value or 0)
    absolute = abs(amount)
    if absolute >= 1_000_000_000_000:
        return f"Rp {amount / 1_000_000_000_000:,.2f} T".replace(",", "_").replace(".", ",").replace("_", ".")
    if absolute >= 1_000_000_000:
        return f"Rp {amount / 1_000_000_000:,.2f} M".replace(",", "_").replace(".", ",").replace("_", ".")
    if absolute >= 1_000_000:
        return f"Rp {amount / 1_000_000:,.2f} Jt".replace(",", "_").replace(".", ",").replace("_", ".")
    return "Rp " + f"{int(round(amount)):,}".replace(",", ".")


def format_integer(value: float | int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _progress_tone(progress: float) -> str:
    if progress >= .70:
        return "high"
    if progress >= .40:
        return "mid"
    return "low"


def _drawer_token(am_name: str, cbase: str, satker: str) -> str:
    return hashlib.md5(
        f"{am_name}|{cbase}|{satker}".encode("utf-8")
    ).hexdigest()[:12]


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="pot-title">{escape(title)}</div><div class="pot-subtitle">{escape(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "") -> None:
    subtitle_html = f'<div class="pot-section-sub">{escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="pot-section-title">{escape(title)}</div>{subtitle_html}',
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: Mapping[str, float | int]) -> None:
    total_meta = f'{format_integer(metrics["paket_total"])} paket · {format_integer(metrics["cbase"])} CBASE'
    belum_pct = metrics["belum"] / metrics["total"] * 100 if metrics["total"] else 0
    belum_meta = f'{format_integer(metrics["paket_belum"])} paket · {belum_pct:.1f}% dari total'
    sudah_meta = f'{format_integer(metrics["paket_sudah"])} paket · {metrics["progress"] * 100:.1f}% dari total'
    st.markdown(
        f"""
        <div class="metric-grid">
          <div class="metric-card">
            <div class="metric-label">Total Pagu</div>
            <div class="metric-value">{format_rupiah(metrics['total'])}</div>
            <div class="metric-meta">{total_meta}</div>
          </div>
          <div class="metric-card belum">
            <div class="metric-label">Belum Pengadaan</div>
            <div class="metric-value">{format_rupiah(metrics['belum'])}</div>
            <div class="metric-meta">{belum_meta}</div>
            <div class="metric-callout">Potensi yang perlu dikejar</div>
          </div>
          <div class="metric-card sudah">
            <div class="metric-label">Sudah Pengadaan</div>
            <div class="metric-value">{format_rupiah(metrics['sudah'])}</div>
            <div class="metric-meta">{sudah_meta}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress(metrics: Mapping[str, float | int]) -> None:
    pct = max(0.0, min(float(metrics["progress"]), 1.0))
    st.markdown(
        f"""
        <div class="progress-wrap">
          <div class="progress-head">
            <div class="progress-title">Progress Pengadaan berdasarkan nilai PAGU</div>
            <div class="progress-pct">{pct * 100:.1f}%</div>
          </div>
          <div class="progress-track"><div class="progress-fill" style="width:{pct * 100:.2f}%"></div></div>
          <div class="progress-legend">
            <span>Sudah pengadaan: <strong>{format_rupiah(metrics['sudah'])}</strong></span>
            <span>Sisa potensi: <strong>{format_rupiah(metrics['belum'])}</strong></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_portfolio_card(row: pd.Series) -> None:
    progress = max(0.0, min(float(row["PROGRESS"]), 1.0))
    st.markdown(
        f"""
        <div class="portfolio-card">
          <div class="portfolio-name">{escape(str(row['PORTOFOLIO']))}</div>
          <div class="portfolio-row"><span>Total Pagu</span><strong>{format_rupiah(row['TOTAL_PAGU'])}</strong></div>
          <div class="portfolio-row belum"><span>Belum</span><strong>{format_rupiah(row['BELUM_PENGADAAN'])}</strong></div>
          <div class="portfolio-row"><span>Sudah</span><strong>{format_rupiah(row['SUDAH_PENGADAAN'])}</strong></div>
          <div class="portfolio-mini-track"><div class="portfolio-mini-fill" style="width:{progress * 100:.2f}%"></div></div>
          <div class="portfolio-progress">Progress {progress * 100:.1f}% · {format_integer(row['PAKET'])} paket</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_pills(metrics: Mapping[str, float | int]) -> None:
    st.markdown(
        f"""
        <div class="info-strip">
          <div class="info-pill"><strong>{format_integer(metrics['cbase'])}</strong> CBASE</div>
          <div class="info-pill"><strong>{format_integer(metrics['satker'])}</strong> SATKER</div>
          <div class="info-pill"><strong>{format_integer(metrics['paket_total'])}</strong> paket</div>
          <div class="info-pill alert"><strong>{format_integer(metrics['paket_belum'])}</strong> paket belum pengadaan</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_total_bar(label: str, package_count: int, total_pagu: int, satker_count: int | None = None) -> None:
    middle = (
        f'<span class="muted">{format_integer(satker_count)} SATKER · {format_integer(package_count)} paket</span>'
        if satker_count is not None
        else f'<span class="muted">{format_integer(package_count)} paket</span>'
    )
    st.markdown(
        f'<div class="total-bar"><span>{escape(label)}</span>{middle}<span>{format_rupiah(total_pagu)}</span></div>',
        unsafe_allow_html=True,
    )


def render_am_accordion_table(am_table: pd.DataFrame, cbase_tables: Mapping[str, pd.DataFrame]) -> None:
    parts: list[str] = [
        '<div class="accordion-shell"><div class="accordion-inner">',
        '<div class="accordion-head overview am-grid">'
        '<div>Account Manager</div><div class="num">Paket</div><div class="num">Total Pagu</div>'
        '<div class="num">Belum Pengadaan</div><div class="num">Sudah Pengadaan</div><div class="num">Progress</div>'
        '</div>',
    ]

    for _, row in am_table.iterrows():
        am_name = str(row["AM"])
        progress = float(row["PROGRESS"])
        tone = _progress_tone(progress)
        cbase_df = cbase_tables.get(am_name, pd.DataFrame())

        parts.append('<details class="pot-accordion">')
        parts.append(
            '<summary class="accordion-summary am-grid">'
            '<div><span class="cell-label"><span class="chevron"></span>'
            f'<span class="label-text">{escape(am_name)}</span>'
            f'<span class="cbase-count-text">{format_integer(row["CBASE"])} Pemkab</span>'
            '</span></div>'
            f'<div class="num">{format_integer(row["PAKET"])}</div>'
            f'<div class="num">{format_rupiah(row["TOTAL_PAGU"])}</div>'
            f'<div class="num highlight-belum">{format_rupiah(row["BELUM_PENGADAAN"])}</div>'
            f'<div class="num highlight-sudah">{format_rupiah(row["SUDAH_PENGADAAN"])}</div>'
            f'<div class="num"><span class="progress-chip {tone}">{progress * 100:.1f}%</span></div>'
            '</summary>'
        )
        parts.append('<div class="accordion-body-flat">')
        for _, cbase_row in cbase_df.iterrows():
            c_progress = float(cbase_row["PROGRESS"])
            c_tone = _progress_tone(c_progress)
            parts.append(
                '<div class="accordion-row am-grid">'
                f'<div class="child-name-cell">{escape(str(cbase_row["CBASE"]))}</div>'
                f'<div class="num">{format_integer(cbase_row["PAKET"])}</div>'
                f'<div class="num">{format_rupiah(cbase_row["TOTAL_PAGU"])}</div>'
                f'<div class="num highlight-belum">{format_rupiah(cbase_row["BELUM_PENGADAAN"])}</div>'
                f'<div class="num highlight-sudah">{format_rupiah(cbase_row["SUDAH_PENGADAAN"])}</div>'
                f'<div class="num"><span class="progress-chip {c_tone}">{c_progress * 100:.1f}%</span></div>'
                '</div>'
            )
        parts.append('</div></details>')

    parts.append('</div></div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_cbase_accordion_table(
    cbase_table: pd.DataFrame,
    satker_tables: Mapping[str, pd.DataFrame],
    am_name: str,
    satker_detail_tables: Mapping[tuple[str, str], pd.DataFrame] | None = None,
) -> None:
    """Render the CBASE hierarchy and pre-render every SATKER drawer.

    Because the drawer HTML is already present on the page, clicking a SATKER
    only changes the URL fragment. The page does not rerun and its scroll
    position stays at the clicked SATKER row.
    """
    detail_lookup = satker_detail_tables or {}
    parts: list[str] = [
        '<div id="potensi-cbase-table" class="accordion-shell"><div class="accordion-inner">',
        '<div class="accordion-head operational cbase-grid">'
        '<div>Government Customer / CBASE</div><div class="num">SATKER</div>'
        '<div class="num">Paket</div><div class="num">Total Pagu</div>'
        '</div>',
    ]
    drawers: list[str] = []

    for _, row in cbase_table.iterrows():
        cbase_key = str(row["CBASE_KEY"])
        cbase_name = str(row["CBASE"])
        satker_df = satker_tables.get(cbase_key, pd.DataFrame())

        parts.append('<details class="pot-accordion">')
        parts.append(
            '<summary class="accordion-summary cbase-grid">'
            '<div><span class="cell-label"><span class="chevron"></span>'
            f'<span class="label-text">{escape(cbase_name)}</span></span></div>'
            f'<div class="num">{format_integer(row["SATKER"])}</div>'
            f'<div class="num">{format_integer(row["PAKET"])}</div>'
            f'<div class="num">{format_rupiah(row["TOTAL_PAGU"])}</div>'
            '</summary>'
        )
        parts.append('<div class="accordion-body-flat">')

        for _, satker_row in satker_df.iterrows():
            satker_name = str(satker_row["SATKER"])
            token = _drawer_token(am_name, cbase_name, satker_name)
            row_anchor = f"satker-row-{token}"
            drawer_id = f"satker-drawer-{token}"
            satker_data = detail_lookup.get(
                (cbase_key, satker_name),
                pd.DataFrame(),
            )

            parts.append(
                f'<div id="{row_anchor}" class="accordion-row cbase-grid satker-row-anchor">'
                '<div class="child-name-cell">'
                f'<a class="satker-link" href="#{drawer_id}">{escape(satker_name)}</a>'
                '</div>'
                '<div class="num child-empty">—</div>'
                f'<div class="num">{format_integer(satker_row["PAKET"])}</div>'
                f'<div class="num">{format_rupiah(satker_row["TOTAL_PAGU"])}</div>'
                '</div>'
            )

            if not satker_data.empty:
                drawers.append(
                    _build_satker_drawer_html(
                        satker_data=satker_data,
                        cbase=cbase_name,
                        satker=satker_name,
                        am_name=am_name,
                        drawer_id=drawer_id,
                        close_anchor=row_anchor,
                    )
                )

        parts.append('</div></details>')

    parts.append('</div></div>')
    parts.extend(drawers)
    st.markdown("".join(parts), unsafe_allow_html=True)


def _portfolio_options_for_drawer(df: pd.DataFrame) -> list[str]:
    order = ["Network", "Device", "Application", "Service", "Media"]
    available = set(df["PORTOFOLIO"].dropna().astype(str).tolist())
    ordered = [name for name in order if name in available]
    ordered.extend(sorted(available.difference(ordered)))
    return ["Semua Portofolio", *ordered]


def _build_drawer_table(detail: pd.DataFrame) -> str:
    detail = detail[["NAMA_PAKET", "PORTOFOLIO", "PAGU"]].copy()
    detail["PAGU"] = pd.to_numeric(detail["PAGU"], errors="coerce").fillna(0)
    detail = detail.sort_values(["PAGU", "NAMA_PAKET"], ascending=[False, True])

    total_pagu = int(detail["PAGU"].sum()) if not detail.empty else 0
    total_paket = len(detail)
    summary = (
        '<div class="drawer-summary">'
        '<div class="drawer-mini-card"><div class="drawer-mini-label">Total Paket</div>'
        f'<div class="drawer-mini-value">{format_integer(total_paket)}</div></div>'
        '<div class="drawer-mini-card"><div class="drawer-mini-label">Total Pagu</div>'
        f'<div class="drawer-mini-value">{format_rupiah(total_pagu)}</div></div></div>'
    )

    if detail.empty:
        return summary + '<div class="drawer-table"><div class="drawer-empty">Tidak ada paket pada filter ini.</div></div>'

    rows: list[str] = []
    for _, row in detail.iterrows():
        portfolio = str(row["PORTOFOLIO"])
        badge_class = portfolio.lower().strip()
        if badge_class not in {"network", "device", "application", "service", "media"}:
            badge_class = "other"
        rows.append(
            '<div class="drawer-table-row">'
            f'<div class="package-name">{escape(str(row["NAMA_PAKET"]))}</div>'
            f'<div><span class="portfolio-badge {badge_class}">{escape(portfolio)}</span></div>'
            f'<div>{format_rupiah(row["PAGU"])}</div>'
            '</div>'
        )

    return (
        summary
        + '<div class="drawer-table">'
        '<div class="drawer-table-head"><div>Nama Paket</div><div>Portofolio</div><div>Pagu</div></div>'
        + "".join(rows)
        + '<div class="drawer-table-total"><div>GRAND TOTAL</div>'
        f'<div>{format_integer(total_paket)} paket</div><div>{format_rupiah(total_pagu)}</div></div></div>'
    )


def _build_satker_drawer_html(
    satker_data: pd.DataFrame,
    cbase: str,
    satker: str,
    am_name: str,
    drawer_id: str,
    close_anchor: str,
) -> str:
    """Build one hidden, client-side SATKER drawer."""
    token = _drawer_token(am_name, cbase, satker)
    options = _portfolio_options_for_drawer(satker_data)

    inputs: list[str] = []
    labels: list[str] = []
    panels: list[str] = []
    dynamic_css: list[str] = []

    for index, option in enumerate(options):
        slug = (
            "all"
            if option == "Semua Portofolio"
            else re.sub(r"[^a-z0-9]+", "-", option.lower()).strip("-")
        )
        input_id = f"drawer-filter-{token}-{slug}"
        panel_class = f"drawer-panel-{token}-{slug}"
        checked = " checked" if index == 0 else ""

        inputs.append(
            f'<input class="drawer-filter-radio" type="radio" '
            f'name="drawer-filter-{token}" id="{input_id}"{checked}>'
        )
        labels.append(
            f'<label class="drawer-chip-label" for="{input_id}">'
            f'{escape(option)}</label>'
        )

        filtered = (
            satker_data
            if option == "Semua Portofolio"
            else satker_data[satker_data["PORTOFOLIO"] == option]
        )
        panels.append(
            f'<section class="drawer-panel {panel_class}">'
            f'{_build_drawer_table(filtered)}</section>'
        )
        dynamic_css.append(
            f'#{input_id}:checked ~ .drawer-top .drawer-chips '
            f'label[for="{input_id}"]'
            '{color:#fff;border-color:transparent;'
            'background:linear-gradient(90deg,#1e3a8a,#2563eb);'
            'box-shadow:0 5px 14px rgba(32,85,214,.18);}'
            f'#{input_id}:checked ~ .drawer-panels .{panel_class}'
            '{display:block;}'
        )

    # Keep the generated drawer markup on one line. Markdown treats lines
    # indented by four spaces as a code block, which previously made the
    # hidden drawer HTML appear as visible text below the CBASE table.
    return (
        f'<section id="{drawer_id}" class="instant-drawer">'
        f'<style>{"".join(dynamic_css)}</style>'
        f'<a class="drawer-overlay" href="#{close_anchor}" '
        'aria-label="Tutup detail paket"></a>'
        '<aside class="satker-drawer">'
        '<div class="drawer-filter-shell">'
        f'{"".join(inputs)}'
        '<div class="drawer-top">'
        '<div class="drawer-actions">'
        f'<a class="drawer-back" href="#{close_anchor}">'
        '← Kembali ke SATKER</a>'
        f'<a class="drawer-close" href="#{close_anchor}" '
        'aria-label="Tutup">×</a>'
        '</div>'
        f'<div class="drawer-heading">{escape(satker)}</div>'
        f'<div class="drawer-sub">{escape(cbase)} · {escape(am_name)}</div>'
        '<div class="drawer-filter-label">Filter Portofolio</div>'
        f'<div class="drawer-chips">{"".join(labels)}</div>'
        '</div>'
        f'<div class="drawer-panels">{"".join(panels)}</div>'
        '</div>'
        '</aside>'
        '</section>'
    )


def render_satker_drawer(
    satker_data: pd.DataFrame,
    cbase: str,
    satker: str,
    am_name: str,
) -> None:
    """Backward-compatible standalone drawer renderer."""
    token = _drawer_token(am_name, cbase, satker)
    st.markdown(
        _build_satker_drawer_html(
            satker_data=satker_data,
            cbase=cbase,
            satker=satker,
            am_name=am_name,
            drawer_id=f"satker-drawer-{token}",
            close_anchor="potensi-cbase-table",
        ),
        unsafe_allow_html=True,
    )
