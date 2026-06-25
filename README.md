# 📊 Data Warehouse — Nilai Akademik Mahasiswa

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![SQLite](https://img.shields.io/badge/Database-SQLite-green?style=flat&logo=sqlite)
![Jupyter](https://img.shields.io/badge/Notebook-Jupyter-orange?style=flat&logo=jupyter)
![Chart.js](https://img.shields.io/badge/Dashboard-Chart.js-ff6384?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

> **Implementasi Data Warehouse** untuk pemantauan nilai akademik mahasiswa Program Studi Sains Data,
> Universitas Brawijaya, Tahun Akademik 2025/2026.

🔗 **[Lihat Dashboard Online →](https://arsa-nth.github.io/academic-dwh-dashboard)**

---

## 🎯 Overview

Project ini membangun sebuah **Data Warehouse** berbasis arsitektur Kimball (Bottom-Up) dengan skema
logis **Star Schema** untuk mengkonsolidasikan data nilai akademik mahasiswa yang sebelumnya tersebar
di berbagai file Excel menjadi satu _Single Source of Truth_.

### Fitur Utama
- **ETL Pipeline** otomatis dari 4 file Excel (3 presensi praktikum + 1 nilai teori)
- **Star Schema** dengan 4 tabel dimensi dan 1 tabel fakta
- **Dashboard analitik** premium (dark mode) dengan 5 visualisasi interaktif
- **Anonimisasi privasi** — nama & NIM mahasiswa disamarkan di output publik
- **Website statis** siap deploy ke GitHub Pages

---

## 📁 Struktur Folder

```
DWH Dosen/
├── 📓 DWH_Dashboard_Notebook.ipynb   ← Notebook utama (run this!)
├── 📄 README.md
├── 📄 requirements.txt
│
├── 📁 data/
│   ├── dwh_nilai_anon.db             ← Database anonim (SQLite)
│   └── raw/                          ← File Excel sumber (tidak diubah)
│
├── 📁 sql/
│   ├── schema.sql                    ← DDL Star Schema
│   └── dwh_queries.sql               ← 6 query analitik
│
├── 📁 src/
│   ├── etl_pipeline.py               ← ETL pipeline (MySQL)
│   ├── generate_charts.py            ← Generator chart matplotlib
│   ├── build_final_report.py         ← Generator laporan DOCX
│   ├── generate_docx_report.py       ← Generator laporan DOCX (simple)
│   ├── anonymize_db.py               ← Script anonimisasi data
│   └── make_notebook.py              ← Generator notebook
│
├── 📁 output/
│   ├── charts/                       ← Chart PNG yang dihasilkan
│   └── reports/                      ← Laporan DOCX & PDF
│
├── 📁 assets/
│   ├── Star Schema.png
│   ├── DWH Alur drawio.png
│   └── _ub_logo.png
│
└── 📁 docs/                          ← Website GitHub Pages
    ├── index.html
    ├── style.css
    ├── app.js
    └── data/
        └── dashboard_data.json       ← Data anonim untuk chart
```

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Notebook

Buka `DWH_Dashboard_Notebook.ipynb` di Jupyter dan jalankan semua cell:

```bash
jupyter notebook DWH_Dashboard_Notebook.ipynb
```

Notebook akan:
1. ✅ Memverifikasi database anonim (`data/dwh_nilai_anon.db`)
2. 📊 Menampilkan query analitik dengan output tabel
3. 📈 Men-generate 5 chart premium dark mode
4. 💾 Menyimpan semua chart ke `output/charts/`

### 3. Lihat Website Lokal

```bash
cd docs
python -m http.server 8000
# Buka http://localhost:8000
```

> **Catatan:** Website membutuhkan server lokal agar fetch JSON berfungsi.
> Gunakan `python -m http.server` atau extension Live Server di VSCode.

### 4. Push ke GitHub & Aktifkan GitHub Pages

```bash
# 1. Buat repo baru di https://github.com/new
#    Nama repo: academic-dwh-dashboard
#    Visibility: Public

# 2. Di folder project ini, jalankan:
git init
git add .
git commit -m "feat: Data Warehouse Dashboard - Nilai Akademik Sains Data UB"
git branch -M main
git remote add origin https://github.com/Arsa-nth/academic-dwh-dashboard.git
git push -u origin main
```

**Aktifkan GitHub Pages:**
- Buka: `https://github.com/Arsa-nth/academic-dwh-dashboard/settings/pages`
- Source: **Deploy from a branch**
- Branch: `main` · Folder: **`/docs`**
- Save → tunggu ~2 menit

✅ Website akan live di: **https://arsa-nth.github.io/academic-dwh-dashboard**

---

## 🗄️ Arsitektur Data Warehouse

### Star Schema

```
         ┌─────────────────┐
         │  Dim_Mahasiswa  │
         └────────┬────────┘
                  │
┌──────────┐      │      ┌────────────────────┐
│Dim_Matkul├──────┼──────┤   Fact_Nilai        │
└──────────┘      │      │ • nilai_angka       │
                  │      │ • tipe_kelas        │
┌─────────────┐   │      │ • status_nilai      │
│Dim_Komponen ├───┘      └────────────────────┘
└─────────────┘                   │
                  ┌───────────────┘
         ┌────────┴────────┐
         │   Dim_Periode   │
         └─────────────────┘
```

### Pembobotan Nilai

| Komponen  | Bobot | Tipe       |
|-----------|-------|------------|
| Tugas 1   | 15%   | Praktikum  |
| Tugas 2   | 15%   | Praktikum  |
| Presensi  | 15%   | Praktikum  |
| Sikap     | 5%    | Praktikum  |
| UTP/Kuis  | 20%   | Praktikum  |
| UAP/Ujian | 30%   | Praktikum  |
| Kuis 1    | 10%   | Teori      |
| Kuis 2    | 10%   | Teori      |
| UTS       | 40%   | Teori      |
| UAS       | 40%   | Teori      |

---

## 📊 Visualisasi

| Chart | Judul | Jenis |
|-------|-------|-------|
| 1 | Progress Kelengkapan Data | Stacked Horizontal Bar |
| 2 | Distribusi Nilai: Teori vs Praktikum | Violin + Box Plot |
| 3 | Rata-rata Nilai per Mata Kuliah | Grouped Bar |
| 4 | Distribusi Komponen Praktikum | Box Plot |
| 5 | Top 10 Nilai Akhir Praktikum | Horizontal Bar (Anonim) |

---

## 🔒 Privasi Data

> Seluruh nama dan NIM mahasiswa yang tercantum dalam output publik ini
> **telah dianonimkan** (contoh: `Mahasiswa 01`, `STD2500001`).
> File Excel sumber data tidak dipublikasikan dan tidak dimodifikasi.

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Database | SQLite (demo), MySQL (produksi) |
| ETL | Python 3.11, Pandas, SQLAlchemy |
| Visualisasi | Matplotlib, Seaborn |
| Notebook | Jupyter Notebook |
| Website | HTML5, CSS3, Chart.js |
| Deployment | GitHub Pages |

---

## 📚 Referensi

- Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*. Wiley.
- Inmon, W. H. (2005). *Building the Data Warehouse*. Wiley.
- McKinney, W. (2010). Data Structures for Statistical Computing in Python. *Proc. 9th Python in Science Conf.*

---

## 👤 Author

**Nathanael Komang Bagus Prakarsa**
- NIM: 245091107111005
- Program Studi Sains Data
- Departemen Statistika, Fakultas Sains, Teknologi, dan Matematika
- Universitas Brawijaya | 2026
- GitHub: [github.com/Arsa-nth](https://github.com/Arsa-nth)

---

*Proyek ini dibuat untuk memenuhi tugas Project-Based Learning Data Warehouse*
*dan sebagai portofolio kompetensi dalam bidang Data Engineering.*
