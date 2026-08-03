# Dashboard Potensi SiRUP — Versi 1

Dashboard Streamlit ini membaca worksheet publik `SIRUP0726` dari Google Sheets:

`https://docs.google.com/spreadsheets/d/1oKB-kUHCSLdU-DI9BpyctduuoQnfA_Kg7m8y5imAYWA/edit`

## Fitur yang sudah dibuat

- Overview: Total Pagu, Belum Pengadaan, Sudah Pengadaan, dan progress.
- Breakdown nilai per portofolio.
- Ringkasan expandable per AM dan CBASE.
- Sidebar AM otomatis diurutkan berdasarkan progress `Sudah / Total Pagu`.
- Section AM dengan card dan progress.
- CBASE expandable berisi tabel `SATKER | PAKET | TOTAL PAGU`.
- Klik baris SATKER membuka panel detail paket dari kanan.
- Detail paket memiliki filter portofolio serta Grand Total.
- Semua tabel PAGU diurutkan dari nilai terbesar.
- Status selain Belum/Sudah, termasuk `Take Out`, tidak masuk perhitungan sehingga `Total = Belum + Sudah`.
- Cache Google Sheets 10 menit dan tombol Perbarui Data.

## Menjalankan secara lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tidak memerlukan `secrets.toml` selama Google Sheets tetap dapat dilihat oleh siapa pun yang memiliki link.

## Deploy ke Streamlit Community Cloud

1. Upload seluruh folder ini ke repository GitHub.
2. Buka Streamlit Community Cloud.
3. Pilih repository dan arahkan main file ke `app.py`.
4. Deploy.

## Sumber mapping AM

Kolom `AM` pada `SIRUP0726` tetap menjadi sumber utama. Bila formula AM kosong atau `UNMAPPED`, kode mencoba mengambil mapping terbaru dari worksheet `MAPPING AM 2026` sebagai fallback.
