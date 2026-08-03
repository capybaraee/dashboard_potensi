from __future__ import annotations

import pandas as pd

BELUM = "Belum Pengadaan"
SUDAH = "Sudah Ada Pengadaan"


def pending_potential(df: pd.DataFrame) -> pd.DataFrame:
    """Return only packages that are still categorized as Belum Pengadaan."""
    if df.empty:
        return df.copy()
    return df[df["STATUS_PENGADAAN"] == BELUM].copy()


def package_count(df: pd.DataFrame) -> int:
    return int(df["PACKAGE_KEY"].nunique()) if not df.empty else 0


def summary_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    total = int(df["PAGU"].sum()) if not df.empty else 0
    belum_df = df[df["STATUS_PENGADAAN"] == BELUM]
    sudah_df = df[df["STATUS_PENGADAAN"] == SUDAH]
    belum = int(belum_df["PAGU"].sum())
    sudah = int(sudah_df["PAGU"].sum())
    progress = (sudah / total) if total else 0.0
    return {
        "total": total,
        "belum": belum,
        "sudah": sudah,
        "progress": progress,
        "paket_total": package_count(df),
        "paket_belum": package_count(belum_df),
        "paket_sudah": package_count(sudah_df),
        "cbase": int(df["CBASE_KEY"].nunique()) if not df.empty else 0,
        "satker": int(df["SATKER"].nunique()) if not df.empty else 0,
    }


def portfolio_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for portfolio, group in df.groupby("PORTOFOLIO", dropna=False):
        metrics = summary_metrics(group)
        rows.append(
            {
                "PORTOFOLIO": str(portfolio),
                "TOTAL_PAGU": int(metrics["total"]),
                "BELUM_PENGADAAN": int(metrics["belum"]),
                "SUDAH_PENGADAAN": int(metrics["sudah"]),
                "PROGRESS": float(metrics["progress"]),
                "PAKET": int(metrics["paket_total"]),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(
        ["BELUM_PENGADAAN", "TOTAL_PAGU"], ascending=[False, False]
    ).reset_index(drop=True)


def am_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for am, group in df.groupby("AM", dropna=False):
        metrics = summary_metrics(group)
        rows.append(
            {
                "AM": str(am),
                "CBASE": int(metrics["cbase"]),
                "PAKET": int(metrics["paket_total"]),
                "TOTAL_PAGU": int(metrics["total"]),
                "BELUM_PENGADAAN": int(metrics["belum"]),
                "SUDAH_PENGADAAN": int(metrics["sudah"]),
                "PROGRESS": float(metrics["progress"]),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(
        ["PROGRESS", "TOTAL_PAGU"], ascending=[False, False]
    ).reset_index(drop=True)


def cbase_status_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for (cbase_key, cbase), group in df.groupby(["CBASE_KEY", "CBASE"], dropna=False):
        metrics = summary_metrics(group)
        rows.append(
            {
                "CBASE_KEY": str(cbase_key),
                "CBASE": str(cbase),
                "SATKER": int(metrics["satker"]),
                "PAKET": int(metrics["paket_total"]),
                "TOTAL_PAGU": int(metrics["total"]),
                "BELUM_PENGADAAN": int(metrics["belum"]),
                "SUDAH_PENGADAAN": int(metrics["sudah"]),
                "PROGRESS": float(metrics["progress"]),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(
        ["BELUM_PENGADAAN", "TOTAL_PAGU"], ascending=[False, False]
    ).reset_index(drop=True)


def cbase_operational_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, int | str]] = []
    for (cbase_key, cbase), group in df.groupby(["CBASE_KEY", "CBASE"], dropna=False):
        rows.append(
            {
                "CBASE_KEY": str(cbase_key),
                "CBASE": str(cbase),
                "SATKER": int(group["SATKER"].nunique()),
                "PAKET": package_count(group),
                "TOTAL_PAGU": int(group["PAGU"].sum()),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values("TOTAL_PAGU", ascending=False).reset_index(drop=True)


def satker_operational_summary(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby("SATKER", as_index=False)
        .agg(PAKET=("PACKAGE_KEY", "nunique"), TOTAL_PAGU=("PAGU", "sum"))
        .sort_values("TOTAL_PAGU", ascending=False)
        .reset_index(drop=True)
    )
    result["PAKET"] = result["PAKET"].astype(int)
    result["TOTAL_PAGU"] = result["TOTAL_PAGU"].astype("int64")
    return result


def package_detail(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[["PACKAGE_KEY", "NAMA_PAKET", "PORTOFOLIO", "PAGU"]]
        .drop_duplicates(subset=["PACKAGE_KEY"], keep="first")
        .sort_values("PAGU", ascending=False)
        .reset_index(drop=True)
    )