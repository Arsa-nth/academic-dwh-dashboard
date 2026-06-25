"""Script pembuat notebook Jupyter DWH Dashboard."""
import json, os

BASE = r"d:\Nael\Mata Kuliah Sains Data\.vscode\Kuliah\Semester 4\DWH Dosen"
OUT  = os.path.join(BASE, "DWH_Dashboard_Notebook.ipynb")

def cc(src):
    return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":src}
def mc(src):
    return {"cell_type":"markdown","metadata":{},"source":src}

cells = []

# ── JUDUL ──────────────────────────────────────────────────────────
cells.append(mc(
"# 📊 Data Warehouse Nilai Akademik Mahasiswa\n"
"## Program Studi Sains Data — Universitas Brawijaya — T.A. 2025/2026\n\n"
"**Oleh:** Nathanael Komang Bagus Prakarsa | NIM: 245091107111005\n\n"
"---\n\n"
"Notebook ini adalah **one-stop pipeline** yang mencakup:\n\n"
"1. 🗄️ Inisialisasi & verifikasi database (SQLite, Star Schema)\n"
"2. 📋 Query analitik pada Data Warehouse\n"
"3. 📈 Visualisasi dashboard premium (dark mode)\n"
"4. 💾 Export chart ke folder `output/charts/`\n\n"
"> **Catatan Privasi:** Nama dan NIM mahasiswa telah **dianonimkan**\n"
"> (contoh: *Mahasiswa 01*, *STD2500001*). File Excel asli tidak diubah.\n\n"
"---\n"
))

# ── CELL 0: Install ─────────────────────────────────────────────────
cells.append(mc("## 🔧 Cell 0 — Instalasi Dependencies"))
cells.append(cc(
'import subprocess, sys\n'
'\n'
'packages = ["pandas", "matplotlib", "seaborn", "numpy", "openpyxl", "Pillow"]\n'
'for pkg in packages:\n'
'    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])\n'
'\n'
'print("Semua dependensi siap!")\n'
))

# ── CELL 1: Import & Config ─────────────────────────────────────────
cells.append(mc("## ⚙️ Cell 1 — Import & Konfigurasi"))
cells.append(cc(
'import os, sqlite3, json\n'
'import pandas as pd\n'
'import numpy as np\n'
'import matplotlib\n'
'matplotlib.use("Agg")\n'
'import matplotlib.pyplot as plt\n'
'import matplotlib.gridspec as gridspec\n'
'from matplotlib.patches import FancyBboxPatch\n'
'import seaborn as sns\n'
'from IPython.display import display, Image as IPyImage\n'
'\n'
'# ─── PATH ─────────────────────────────────────────────────────────\n'
'BASE_DIR      = os.path.abspath(os.path.dirname("__file__")) if "__file__" in dir() else os.getcwd()\n'
'DB_PATH       = os.path.join(BASE_DIR, "data", "dwh_nilai_anon.db")\n'
'OUTPUT_CHARTS = os.path.join(BASE_DIR, "output", "charts")\n'
'os.makedirs(OUTPUT_CHARTS, exist_ok=True)\n'
'\n'
'print(f"Working dir : {BASE_DIR}")\n'
'print(f"DB path     : {DB_PATH}")\n'
'print(f"DB ditemukan: {os.path.exists(DB_PATH)}")\n'
))

# ── CELL 2: Design System ───────────────────────────────────────────
cells.append(mc("## 🎨 Cell 2 — Design System (Dark Mode)"))
cells.append(cc(
'BG_COLOR      = "#0F0F13"\n'
'CARD_COLOR    = "#1A1A24"\n'
'PANEL_COLOR   = "#22222E"\n'
'TEXT_COLOR    = "#E8E8F0"\n'
'ACCENT_BLUE   = "#4F8EF7"\n'
'ACCENT_PURPLE = "#9B72F5"\n'
'ACCENT_GREEN  = "#22D3A3"\n'
'ACCENT_YELLOW = "#FBBF24"\n'
'ACCENT_RED    = "#F87171"\n'
'ACCENT_CYAN   = "#38BDF8"\n'
'ACCENT_ORANGE = "#FB923C"\n'
'GRID_COLOR    = "#2A2A38"\n'
'\n'
'plt.rcParams.update({\n'
'    "figure.facecolor" : BG_COLOR,\n'
'    "axes.facecolor"   : CARD_COLOR,\n'
'    "text.color"       : TEXT_COLOR,\n'
'    "axes.labelcolor"  : TEXT_COLOR,\n'
'    "xtick.color"      : TEXT_COLOR,\n'
'    "ytick.color"      : TEXT_COLOR,\n'
'    "font.family"      : "DejaVu Sans",\n'
'    "grid.color"       : GRID_COLOR,\n'
'    "grid.linestyle"   : "--",\n'
'    "grid.linewidth"   : 0.5,\n'
'    "axes.edgecolor"   : GRID_COLOR,\n'
'    "axes.spines.top"  : False,\n'
'    "axes.spines.right": False,\n'
'})\n'
'print("Design system siap!")\n'
))

# ── CELL 3: KPI Query ───────────────────────────────────────────────
cells.append(mc(
"## 📊 Cell 3 — Query Analitik & KPI\n\n"
"**Star Schema** yang digunakan:\n\n"
"```\n"
"Dim_Mahasiswa ─────┐\n"
"Dim_MataKuliah ────┼──► Fact_Nilai\n"
"Dim_KomponenNilai ─┤\n"
"Dim_Periode ───────┘\n"
"```\n"
))
cells.append(cc(
'conn = sqlite3.connect(DB_PATH)\n'
'\n'
'# ── Q6: KPI ────────────────────────────────────────────────────────\n'
'kpi = pd.read_sql_query("""\n'
'    SELECT\n'
'        (SELECT COUNT(DISTINCT mahasiswa_id) FROM Dim_Mahasiswa)        AS total_mahasiswa,\n'
'        (SELECT COUNT(*) FROM Fact_Nilai)                               AS total_records,\n'
'        (SELECT COUNT(*) FROM Fact_Nilai WHERE status_nilai=\'lengkap\') AS total_lengkap,\n'
'        (SELECT ROUND(AVG(nilai_angka),2) FROM Fact_Nilai\n'
'         WHERE status_nilai=\'lengkap\')                                 AS avg_overall,\n'
'        (SELECT ROUND(AVG(nilai_angka),2) FROM Fact_Nilai\n'
'         WHERE status_nilai=\'lengkap\' AND tipe_kelas=\'praktikum\')     AS avg_praktikum,\n'
'        (SELECT ROUND(AVG(nilai_angka),2) FROM Fact_Nilai\n'
'         WHERE status_nilai=\'lengkap\' AND tipe_kelas=\'teori\')         AS avg_teori\n'
'""", conn)\n'
'\n'
'print("=" * 50)\n'
'print("  KEY PERFORMANCE INDICATORS")\n'
'print("=" * 50)\n'
'display(kpi.T.rename(columns={0: "Nilai"}))\n'
'\n'
'# ── Q1: Progress ───────────────────────────────────────────────────\n'
'df_progress = pd.read_sql_query("""\n'
'    SELECT tipe_kelas, status_nilai, COUNT(*) AS jumlah\n'
'    FROM Fact_Nilai GROUP BY tipe_kelas, status_nilai\n'
'""", conn)\n'
'print("\\n=== Q1: PROGRESS KELENGKAPAN DATA ===")\n'
'display(df_progress)\n'
'\n'
'# ── Q3: Rata-rata per matkul ───────────────────────────────────────\n'
'df_matkul = pd.read_sql_query("""\n'
'    SELECT mk.nama_matkul, f.tipe_kelas,\n'
'           ROUND(AVG(f.nilai_angka),2) AS rata_rata,\n'
'           COUNT(DISTINCT f.mahasiswa_id) AS jml_mhs\n'
'    FROM Fact_Nilai f\n'
'    JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id\n'
'    WHERE f.status_nilai = \'lengkap\'\n'
'    GROUP BY mk.matkul_id, f.tipe_kelas ORDER BY mk.nama_matkul\n'
'""", conn)\n'
'print("\\n=== Q3: RATA-RATA NILAI PER MATA KULIAH ===")\n'
'display(df_matkul)\n'
'\n'
'# ── Q4: Komponen Praktikum ─────────────────────────────────────────\n'
'df_komponen = pd.read_sql_query("""\n'
'    SELECT mk.nama_matkul, k.nama_komponen, k.bobot_persen,\n'
'           ROUND(AVG(f.nilai_angka),2) AS rata_rata, COUNT(f.nilai_angka) AS n\n'
'    FROM Fact_Nilai f\n'
'    JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id\n'
'    JOIN Dim_KomponenNilai k ON f.komponen_id = k.komponen_id\n'
'    WHERE f.status_nilai = \'lengkap\' AND f.tipe_kelas = \'praktikum\'\n'
'    GROUP BY mk.matkul_id, k.komponen_id\n'
'""", conn)\n'
'print("\\n=== Q4: KOMPONEN PRAKTIKUM ===")\n'
'display(df_komponen)\n'
'\n'
'# ── Q5: Top 10 ─────────────────────────────────────────────────────\n'
'df_top10 = pd.read_sql_query("""\n'
'    SELECT m.nama AS nama_mahasiswa, mk.nama_matkul,\n'
'           ROUND(SUM(f.nilai_angka * (k.bobot_persen / 100.0)), 2) AS nilai_akhir_estimasi\n'
'    FROM Fact_Nilai f\n'
'    JOIN Dim_Mahasiswa m     ON f.mahasiswa_id = m.mahasiswa_id\n'
'    JOIN Dim_MataKuliah mk   ON f.matkul_id    = mk.matkul_id\n'
'    JOIN Dim_KomponenNilai k ON f.komponen_id  = k.komponen_id\n'
'    WHERE f.tipe_kelas = \'praktikum\' AND f.nilai_angka IS NOT NULL\n'
'    GROUP BY m.mahasiswa_id, mk.matkul_id\n'
'    ORDER BY nilai_akhir_estimasi DESC LIMIT 10\n'
'""", conn)\n'
'print("\\n=== Q5: TOP 10 NILAI AKHIR PRAKTIKUM ===")\n'
'display(df_top10)\n'
'\n'
'conn.close()\n'
))

# ── CELL 4: Chart 1 ─────────────────────────────────────────────────
cells.append(mc("## 📈 Cell 4 — Chart 1: Progress Kelengkapan Data"))
cells.append(cc(
'conn = sqlite3.connect(DB_PATH)\n'
'df1 = pd.read_sql_query(\n'
'    "SELECT tipe_kelas, status_nilai, COUNT(*) AS j FROM Fact_Nilai GROUP BY tipe_kelas, status_nilai",\n'
'    conn); conn.close()\n'
'\n'
'pv = df1.pivot(index="tipe_kelas", columns="status_nilai", values="j").fillna(0)\n'
'for c in ["lengkap","belum_dikoreksi","belum_dilaksanakan"]:\n'
'    if c not in pv.columns: pv[c] = 0\n'
'pv = pv[["lengkap","belum_dikoreksi","belum_dilaksanakan"]]\n'
'pp = pv.div(pv.sum(axis=1), axis=0) * 100\n'
'\n'
'fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=BG_COLOR)\n'
'ax.set_facecolor(CARD_COLOR)\n'
'lefts = np.zeros(len(pp)); yp = np.arange(len(pp))\n'
'colors_bar = [ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED]\n'
'labels_bar = ["Lengkap", "Belum Dikoreksi", "Belum Dilaksanakan"]\n'
'\n'
'for col, clr, lbl in zip(pp.columns, colors_bar, labels_bar):\n'
'    vs = pp[col].values\n'
'    ax.barh(yp, vs, left=lefts, color=clr, height=0.5,\n'
'            edgecolor=BG_COLOR, linewidth=0.8, label=lbl)\n'
'    for idx, (v, l) in enumerate(zip(vs, lefts)):\n'
'        if v > 7:\n'
'            ax.text(l + v/2, idx, f"{v:.1f}%", ha="center", va="center",\n'
'                    color="white", fontsize=10, fontweight="bold")\n'
'    lefts += vs\n'
'\n'
'ax.set_yticks(yp)\n'
'ax.set_yticklabels(["Praktikum", "Teori"], fontsize=12, fontweight="bold")\n'
'ax.set_xlim(0, 100); ax.set_xlabel("Persentase (%)", fontsize=11)\n'
'ax.set_title("Chart 1 — Progress Kelengkapan Data Nilai per Tipe Kelas",\n'
'             fontsize=13, fontweight="bold", pad=15, color=TEXT_COLOR)\n'
'ax.grid(True, axis="x", alpha=0.4)\n'
'lg = ax.legend(loc="lower right", fontsize=9, frameon=True,\n'
'               facecolor=PANEL_COLOR, edgecolor=GRID_COLOR)\n'
'[t.set_color(TEXT_COLOR) for t in lg.get_texts()]\n'
'\n'
'plt.tight_layout()\n'
'p1 = os.path.join(OUTPUT_CHARTS, "chart1_progress.png")\n'
'plt.savefig(p1, dpi=200, facecolor=BG_COLOR, bbox_inches="tight")\n'
'plt.show()\n'
'print(f"Tersimpan: {p1}")\n'
))

# ── CELL 5: Chart 2 ─────────────────────────────────────────────────
cells.append(mc("## 📈 Cell 5 — Chart 2: Distribusi Nilai Teori vs Praktikum"))
cells.append(cc(
'conn = sqlite3.connect(DB_PATH)\n'
'df2 = pd.read_sql_query(\n'
'    "SELECT tipe_kelas, nilai_angka FROM Fact_Nilai"\n'
'    " WHERE status_nilai=\'lengkap\' AND nilai_angka IS NOT NULL", conn)\n'
'conn.close()\n'
'\n'
'fig, ax = plt.subplots(figsize=(8, 5), facecolor=BG_COLOR)\n'
'ax.set_facecolor(CARD_COLOR)\n'
'sns.violinplot(x="tipe_kelas", y="nilai_angka", data=df2,\n'
'               palette={"praktikum": ACCENT_BLUE, "teori": ACCENT_PURPLE},\n'
'               ax=ax, inner="quartile", linewidth=1.2, cut=0.5)\n'
'\n'
'means2 = df2.groupby("tipe_kelas")["nilai_angka"].mean()\n'
'stds2  = df2.groupby("tipe_kelas")["nilai_angka"].std()\n'
'for i, tp in enumerate(["praktikum", "teori"]):\n'
'    if tp in means2.index:\n'
'        ax.scatter(i, means2[tp], color=ACCENT_YELLOW, zorder=5, s=70, marker="D")\n'
'        ax.annotate(f"mean={means2[tp]:.1f}\\nstd={stds2[tp]:.1f}",\n'
'                    xy=(i, means2[tp]), xytext=(i+0.3, means2[tp]+6),\n'
'                    fontsize=9, color=ACCENT_YELLOW, fontweight="bold",\n'
'                    arrowprops=dict(arrowstyle="->", color=ACCENT_YELLOW, lw=1.2),\n'
'                    bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_COLOR,\n'
'                              edgecolor=ACCENT_YELLOW, alpha=0.9))\n'
'\n'
'ax.set_title("Chart 2 — Distribusi Nilai: Teori vs Praktikum",\n'
'             fontsize=13, fontweight="bold", pad=15, color=TEXT_COLOR)\n'
'ax.set_xlabel("Tipe Kelas", fontsize=11)\n'
'ax.set_ylabel("Nilai Angka", fontsize=11)\n'
'ax.set_xticklabels(["Praktikum", "Teori"], fontsize=11, fontweight="bold")\n'
'ax.set_ylim(0, 115); ax.grid(True, axis="y", alpha=0.4)\n'
'\n'
'plt.tight_layout()\n'
'p2 = os.path.join(OUTPUT_CHARTS, "chart2_distribusi.png")\n'
'plt.savefig(p2, dpi=200, facecolor=BG_COLOR, bbox_inches="tight")\n'
'plt.show()\n'
'print(f"Tersimpan: {p2}")\n'
))

# ── CELL 6: Chart 3 ─────────────────────────────────────────────────
cells.append(mc("## 📈 Cell 6 — Chart 3: Rata-rata Nilai per Mata Kuliah"))
cells.append(cc(
'conn = sqlite3.connect(DB_PATH)\n'
'df3 = pd.read_sql_query("""\n'
'    SELECT mk.nama_matkul, f.tipe_kelas,\n'
'           ROUND(AVG(f.nilai_angka),2) AS rata_rata\n'
'    FROM Fact_Nilai f\n'
'    JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id\n'
'    WHERE f.status_nilai = \'lengkap\'\n'
'    GROUP BY mk.matkul_id, f.tipe_kelas\n'
'""", conn); conn.close()\n'
'\n'
'df3["matkul_short"] = (df3["nama_matkul"]\n'
'    .str.replace("Metode ","M.",regex=False)\n'
'    .str.replace("Statistika","Stat.",regex=False)\n'
'    .str.replace("Sains Data","S.D.",regex=False))\n'
'\n'
'fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG_COLOR)\n'
'ax.set_facecolor(CARD_COLOR)\n'
'sns.barplot(x="matkul_short", y="rata_rata", hue="tipe_kelas", data=df3,\n'
'            palette={"praktikum": ACCENT_BLUE, "teori": ACCENT_PURPLE},\n'
'            ax=ax, edgecolor=BG_COLOR, width=0.6)\n'
'\n'
'for p in ax.patches:\n'
'    h = p.get_height()\n'
'    if h > 0:\n'
'        ax.annotate(f"{h:.1f}", (p.get_x()+p.get_width()/2, h+1.5),\n'
'                    ha="center", va="bottom", color=TEXT_COLOR,\n'
'                    fontsize=9.5, fontweight="bold")\n'
'\n'
'ax.axhline(y=80, color=ACCENT_YELLOW, linestyle="--", linewidth=1.2, alpha=0.7)\n'
'ax.text(ax.get_xlim()[1]*0.98, 82, "KKM=80", ha="right",\n'
'        fontsize=9, color=ACCENT_YELLOW, alpha=0.9)\n'
'ax.set_ylim(0, 115)\n'
'ax.set_title("Chart 3 — Rata-rata Nilai per Mata Kuliah",\n'
'             fontsize=13, fontweight="bold", pad=15, color=TEXT_COLOR)\n'
'ax.set_xlabel("Mata Kuliah", fontsize=11); ax.set_ylabel("Rata-rata Nilai", fontsize=11)\n'
'ax.grid(True, axis="y", alpha=0.4)\n'
'lg3 = ax.legend(title="Tipe Kelas", facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, fontsize=9)\n'
'lg3.get_title().set_color(TEXT_COLOR); [t.set_color(TEXT_COLOR) for t in lg3.get_texts()]\n'
'\n'
'plt.tight_layout()\n'
'p3 = os.path.join(OUTPUT_CHARTS, "chart3_matkul.png")\n'
'plt.savefig(p3, dpi=200, facecolor=BG_COLOR, bbox_inches="tight")\n'
'plt.show()\n'
'print(f"Tersimpan: {p3}")\n'
))

# ── CELL 7: Chart 4 ─────────────────────────────────────────────────
cells.append(mc("## 📈 Cell 7 — Chart 4: Distribusi Komponen Praktikum"))
cells.append(cc(
'conn = sqlite3.connect(DB_PATH)\n'
'df4 = pd.read_sql_query("""\n'
'    SELECT mk.nama_matkul, k.nama_komponen, f.nilai_angka\n'
'    FROM Fact_Nilai f\n'
'    JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id\n'
'    JOIN Dim_KomponenNilai k ON f.komponen_id = k.komponen_id\n'
'    WHERE f.status_nilai = \'lengkap\'\n'
'      AND f.tipe_kelas   = \'praktikum\'\n'
'      AND f.nilai_angka IS NOT NULL\n'
'""", conn); conn.close()\n'
'\n'
'valid_komps = ["Tugas 1","Tugas 2","Presensi","Sikap","UTP","UAP"]\n'
'df4 = df4[df4["nama_komponen"].isin(valid_komps)]\n'
'\n'
'fig, ax = plt.subplots(figsize=(11, 5.5), facecolor=BG_COLOR)\n'
'ax.set_facecolor(CARD_COLOR)\n'
'matkul_names = df4["nama_matkul"].unique()\n'
'pal = [ACCENT_BLUE, ACCENT_PURPLE, ACCENT_GREEN][:len(matkul_names)]\n'
'\n'
'sns.boxplot(x="nama_komponen", y="nilai_angka", hue="nama_matkul",\n'
'            data=df4, order=valid_komps, palette=pal, ax=ax, linewidth=1.1,\n'
'            flierprops=dict(marker="o", markerfacecolor=ACCENT_RED,\n'
'                            markersize=4, markeredgecolor=BG_COLOR))\n'
'\n'
'ax.axhline(y=80, color=ACCENT_YELLOW, linestyle="--", linewidth=1.2, alpha=0.7)\n'
'ax.set_ylim(40, 115)\n'
'ax.set_title("Chart 4 — Distribusi Nilai per Komponen Kelas Praktikum",\n'
'             fontsize=13, fontweight="bold", pad=15, color=TEXT_COLOR)\n'
'ax.set_xlabel("Komponen Nilai", fontsize=11); ax.set_ylabel("Nilai Mahasiswa", fontsize=11)\n'
'ax.grid(True, axis="y", alpha=0.4)\n'
'lg4 = ax.legend(title="Mata Kuliah", loc="lower right",\n'
'                facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, fontsize=8.5)\n'
'lg4.get_title().set_color(TEXT_COLOR); [t.set_color(TEXT_COLOR) for t in lg4.get_texts()]\n'
'\n'
'plt.tight_layout()\n'
'p4 = os.path.join(OUTPUT_CHARTS, "chart4_komponen.png")\n'
'plt.savefig(p4, dpi=200, facecolor=BG_COLOR, bbox_inches="tight")\n'
'plt.show()\n'
'print(f"Tersimpan: {p4}")\n'
))

# ── CELL 8: Chart 5 ─────────────────────────────────────────────────
cells.append(mc("## 📈 Cell 8 — Chart 5: Top 10 Mahasiswa (Data Anonim)"))
cells.append(cc(
'conn = sqlite3.connect(DB_PATH)\n'
'df5 = pd.read_sql_query("""\n'
'    SELECT m.nama, mk.nama_matkul,\n'
'           ROUND(SUM(f.nilai_angka*(k.bobot_persen/100.0)),2) AS nilai_akhir\n'
'    FROM Fact_Nilai f\n'
'    JOIN Dim_Mahasiswa m ON f.mahasiswa_id = m.mahasiswa_id\n'
'    JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id\n'
'    JOIN Dim_KomponenNilai k ON f.komponen_id = k.komponen_id\n'
'    WHERE f.tipe_kelas = \'praktikum\' AND f.nilai_angka IS NOT NULL\n'
'    GROUP BY m.mahasiswa_id, mk.matkul_id\n'
'    ORDER BY nilai_akhir DESC LIMIT 10\n'
'""", conn); conn.close()\n'
'\n'
'df5s = df5.sort_values("nilai_akhir", ascending=True)\n'
'df5s["label"] = (df5s["nama"] + "\\n(" +\n'
'    df5s["nama_matkul"].apply(lambda x: "".join([w[0] for w in x.split()])) + ")")\n'
'\n'
'norm = df5s["nilai_akhir"] - df5s["nilai_akhir"].min()\n'
'norm = norm / (norm.max() + 0.01)\n'
'bar_colors = plt.cm.plasma(0.4 + norm.values * 0.5)\n'
'\n'
'fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_COLOR)\n'
'ax.set_facecolor(CARD_COLOR)\n'
'bars = ax.barh(range(len(df5s)), df5s["nilai_akhir"],\n'
'               color=bar_colors, edgecolor=BG_COLOR, linewidth=0.8, height=0.65)\n'
'ax.set_yticks(range(len(df5s)))\n'
'ax.set_yticklabels(df5s["label"].values, fontsize=8.5)\n'
'ax.set_xlim(85, 102)\n'
'ax.set_title("Chart 5 — Top 10 Nilai Akhir Praktikum (Data Dianonimkan)",\n'
'             fontsize=13, fontweight="bold", pad=15, color=TEXT_COLOR)\n'
'ax.set_xlabel("Nilai Akhir Estimasi", fontsize=11)\n'
'ax.grid(True, axis="x", alpha=0.4)\n'
'for bar, val in zip(bars, df5s["nilai_akhir"]):\n'
'    ax.text(val+0.1, bar.get_y()+bar.get_height()/2, f" {val:.2f}",\n'
'            va="center", ha="left", fontsize=9, color=ACCENT_YELLOW, fontweight="bold")\n'
'\n'
'plt.tight_layout()\n'
'p5 = os.path.join(OUTPUT_CHARTS, "chart5_top10_anon.png")\n'
'plt.savefig(p5, dpi=200, facecolor=BG_COLOR, bbox_inches="tight")\n'
'plt.show()\n'
'print(f"Tersimpan: {p5}")\n'
))

# ── CELL 9: Dashboard Terpadu ────────────────────────────────────────
cells.append(mc("## 🖼️ Cell 9 — Export Dashboard Terpadu"))
cells.append(cc(
'# Load semua data\n'
'conn = sqlite3.connect(DB_PATH)\n'
'df_kpi = pd.read_sql_query("""\n'
'    SELECT\n'
'        (SELECT COUNT(DISTINCT mahasiswa_id) FROM Dim_Mahasiswa)        AS total_mhs,\n'
'        (SELECT COUNT(*) FROM Fact_Nilai)                               AS total_records,\n'
'        (SELECT COUNT(*) FROM Fact_Nilai WHERE status_nilai=\'lengkap\') AS total_lengkap,\n'
'        (SELECT ROUND(AVG(nilai_angka),2) FROM Fact_Nilai\n'
'         WHERE status_nilai=\'lengkap\')                                 AS avg_nilai,\n'
'        (SELECT ROUND(AVG(nilai_angka),2) FROM Fact_Nilai\n'
'         WHERE status_nilai=\'lengkap\' AND tipe_kelas=\'praktikum\')     AS avg_prak,\n'
'        (SELECT ROUND(AVG(nilai_angka),2) FROM Fact_Nilai\n'
'         WHERE status_nilai=\'lengkap\' AND tipe_kelas=\'teori\')         AS avg_teori\n'
'""", conn)\n'
'da = pd.read_sql_query("SELECT tipe_kelas,status_nilai,COUNT(*) j FROM Fact_Nilai GROUP BY tipe_kelas,status_nilai", conn)\n'
'db = pd.read_sql_query("SELECT tipe_kelas,nilai_angka FROM Fact_Nilai WHERE status_nilai=\'lengkap\' AND nilai_angka IS NOT NULL", conn)\n'
'dc = pd.read_sql_query("SELECT mk.nama_matkul,f.tipe_kelas,ROUND(AVG(f.nilai_angka),2) r FROM Fact_Nilai f JOIN Dim_MataKuliah mk ON f.matkul_id=mk.matkul_id WHERE f.status_nilai=\'lengkap\' GROUP BY mk.matkul_id,f.tipe_kelas", conn)\n'
'dd = pd.read_sql_query("SELECT mk.nama_matkul,k.nama_komponen,f.nilai_angka FROM Fact_Nilai f JOIN Dim_MataKuliah mk ON f.matkul_id=mk.matkul_id JOIN Dim_KomponenNilai k ON f.komponen_id=k.komponen_id WHERE f.status_nilai=\'lengkap\' AND f.tipe_kelas=\'praktikum\' AND f.nilai_angka IS NOT NULL", conn)\n'
'de = pd.read_sql_query("SELECT m.nama,mk.nama_matkul,ROUND(SUM(f.nilai_angka*(k.bobot_persen/100.0)),2) v FROM Fact_Nilai f JOIN Dim_Mahasiswa m ON f.mahasiswa_id=m.mahasiswa_id JOIN Dim_MataKuliah mk ON f.matkul_id=mk.matkul_id JOIN Dim_KomponenNilai k ON f.komponen_id=k.komponen_id WHERE f.tipe_kelas=\'praktikum\' AND f.nilai_angka IS NOT NULL GROUP BY m.mahasiswa_id,mk.matkul_id ORDER BY v DESC LIMIT 10", conn)\n'
'conn.close()\n'
'\n'
'kpi = df_kpi.iloc[0]\n'
'fig = plt.figure(figsize=(22, 16), facecolor=BG_COLOR)\n'
'\n'
'# Header\n'
'hdr = fig.add_axes([0, 0.94, 1, 0.06])\n'
'hdr.set_facecolor("#1C1C2E"); hdr.axis("off")\n'
'hdr.text(0.5, 0.65, "DASHBOARD ANALITIK  |  Data Warehouse Nilai Akademik Mahasiswa",\n'
'         ha="center", va="center", fontsize=16, fontweight="bold", color="white")\n'
'hdr.text(0.5, 0.18, "Program Studi Sains Data  |  Universitas Brawijaya  |  T.A. 2025/2026  |  Data Anonim",\n'
'         ha="center", va="center", fontsize=9, color="#9999BB")\n'
'\n'
'# KPI Cards\n'
'card_info = [\n'
'    ("Total Mahasiswa",   f"{int(kpi[\'total_mhs\'])}",    ACCENT_BLUE),\n'
'    ("Total Records",     f"{int(kpi[\'total_records\'])}", ACCENT_PURPLE),\n'
'    ("Nilai Lengkap",     f"{int(kpi[\'total_lengkap\'])}", ACCENT_GREEN),\n'
'    ("Avg. Praktikum",    f"{kpi[\'avg_prak\']:.2f}",      ACCENT_YELLOW),\n'
'    ("Avg. Teori",        f"{kpi[\'avg_teori\']:.2f}",     ACCENT_CYAN),\n'
'    ("Avg. Overall",      f"{kpi[\'avg_nilai\']:.2f}",     ACCENT_ORANGE),\n'
']\n'
'for i, (lbl, val, clr) in enumerate(card_info):\n'
'    ca = fig.add_axes([i*(1/6)+0.003, 0.86, (1/6)-0.006, 0.075])\n'
'    ca.set_facecolor(PANEL_COLOR); ca.axis("off")\n'
'    ca.add_patch(FancyBboxPatch((0,0.85),1,0.15,transform=ca.transAxes,\n'
'                                boxstyle="square,pad=0",facecolor=clr,alpha=0.8))\n'
'    ca.text(0.5,0.52,val,ha="center",va="center",fontsize=20,fontweight="bold",color=clr,transform=ca.transAxes)\n'
'    ca.text(0.5,0.18,lbl,ha="center",va="center",fontsize=8.5,color="#AAAACC",transform=ca.transAxes)\n'
'\n'
'gs = gridspec.GridSpec(2,3,left=0.04,right=0.97,top=0.845,bottom=0.04,hspace=0.38,wspace=0.32)\n'
'\n'
'# Chart 1\n'
'ax1=fig.add_subplot(gs[0,0]); ax1.set_facecolor(CARD_COLOR)\n'
'pv=da.pivot(index="tipe_kelas",columns="status_nilai",values="j").fillna(0)\n'
'for c in ["lengkap","belum_dikoreksi","belum_dilaksanakan"]:\n'
'    if c not in pv.columns: pv[c]=0\n'
'pp=pv[["lengkap","belum_dikoreksi","belum_dilaksanakan"]].div(pv.sum(axis=1),axis=0)*100\n'
'lefts=np.zeros(len(pp)); yp=np.arange(len(pp))\n'
'for col,clr in zip(pp.columns,[ACCENT_GREEN,ACCENT_YELLOW,ACCENT_RED]):\n'
'    vs=pp[col].values; ax1.barh(yp,vs,left=lefts,color=clr,height=0.5,edgecolor=BG_COLOR,label=col.replace("_"," ").title())\n'
'    for idx,(v,l) in enumerate(zip(vs,lefts)):\n'
'        if v>8: ax1.text(l+v/2,idx,f"{v:.1f}%",ha="center",va="center",color="white",fontsize=9,fontweight="bold")\n'
'    lefts+=vs\n'
'ax1.set_yticks(yp); ax1.set_yticklabels(["Praktikum","Teori"],fontsize=10,fontweight="bold")\n'
'ax1.set_xlim(0,100); ax1.set_xlabel("%",fontsize=9); ax1.grid(True,axis="x",alpha=0.4)\n'
'ax1.set_title("Progress Kelengkapan Data",fontsize=11,fontweight="bold",pad=10,color=TEXT_COLOR)\n'
'l1=ax1.legend(loc="lower right",fontsize=7,frameon=True,facecolor=PANEL_COLOR,edgecolor=GRID_COLOR)\n'
'[t.set_color(TEXT_COLOR) for t in l1.get_texts()]\n'
'\n'
'# Chart 2\n'
'ax2=fig.add_subplot(gs[0,1]); ax2.set_facecolor(CARD_COLOR)\n'
'sns.violinplot(x="tipe_kelas",y="nilai_angka",data=db,\n'
'               palette={"praktikum":ACCENT_BLUE,"teori":ACCENT_PURPLE},\n'
'               ax=ax2,inner="quartile",linewidth=1.2,cut=0.5)\n'
'm2=db.groupby("tipe_kelas")["nilai_angka"].mean(); s2=db.groupby("tipe_kelas")["nilai_angka"].std()\n'
'for i,tp in enumerate(["praktikum","teori"]):\n'
'    if tp in m2.index:\n'
'        ax2.scatter(i,m2[tp],color=ACCENT_YELLOW,zorder=5,s=60,marker="D")\n'
'        ax2.annotate(f"mean={m2[tp]:.1f}\\nstd={s2[tp]:.1f}",xy=(i,m2[tp]),xytext=(i+0.3,m2[tp]+6),\n'
'                     fontsize=8,color=ACCENT_YELLOW,fontweight="bold",\n'
'                     arrowprops=dict(arrowstyle="->",color=ACCENT_YELLOW,lw=1),\n'
'                     bbox=dict(boxstyle="round,pad=0.3",facecolor=PANEL_COLOR,edgecolor=ACCENT_YELLOW,alpha=0.85))\n'
'ax2.set_title("Distribusi Nilai: Teori vs Praktikum",fontsize=11,fontweight="bold",pad=10,color=TEXT_COLOR)\n'
'ax2.set_xlabel("Tipe Kelas",fontsize=9); ax2.set_ylabel("Nilai",fontsize=9)\n'
'ax2.set_xticklabels(["Praktikum","Teori"],fontsize=10,fontweight="bold")\n'
'ax2.set_ylim(0,115); ax2.grid(True,axis="y",alpha=0.4)\n'
'\n'
'# Chart 3\n'
'ax3=fig.add_subplot(gs[0,2]); ax3.set_facecolor(CARD_COLOR)\n'
'dc["ms"]=(dc["nama_matkul"].str.replace("Metode ","M.",regex=False)\n'
'          .str.replace("Statistika","Stat.",regex=False).str.replace("Sains Data","S.D.",regex=False))\n'
'sns.barplot(x="ms",y="r",hue="tipe_kelas",data=dc,\n'
'            palette={"praktikum":ACCENT_BLUE,"teori":ACCENT_PURPLE},ax=ax3,edgecolor=BG_COLOR,width=0.6)\n'
'for p in ax3.patches:\n'
'    h=p.get_height()\n'
'    if h>0: ax3.annotate(f"{h:.1f}",(p.get_x()+p.get_width()/2,h+1),ha="center",va="bottom",color=TEXT_COLOR,fontsize=8.5,fontweight="bold")\n'
'ax3.axhline(y=80,color=ACCENT_YELLOW,linestyle="--",linewidth=1,alpha=0.7)\n'
'ax3.set_ylim(0,115); ax3.set_title("Rata-rata Nilai per Mata Kuliah",fontsize=11,fontweight="bold",pad=10,color=TEXT_COLOR)\n'
'ax3.set_xlabel("",fontsize=9); ax3.set_ylabel("Rata-rata",fontsize=9); ax3.grid(True,axis="y",alpha=0.4)\n'
'l3=ax3.legend(title="Tipe",facecolor=PANEL_COLOR,edgecolor=GRID_COLOR,fontsize=8); l3.get_title().set_color(TEXT_COLOR)\n'
'[t.set_color(TEXT_COLOR) for t in l3.get_texts()]\n'
'\n'
'# Chart 4\n'
'ax4=fig.add_subplot(gs[1,0:2]); ax4.set_facecolor(CARD_COLOR)\n'
'vk=["Tugas 1","Tugas 2","Presensi","Sikap","UTP","UAP"]\n'
'df4f=dd[dd["nama_komponen"].isin(vk)]\n'
'mn=df4f["nama_matkul"].unique()\n'
'sns.boxplot(x="nama_komponen",y="nilai_angka",hue="nama_matkul",data=df4f,order=vk,\n'
'            palette=[ACCENT_BLUE,ACCENT_PURPLE,ACCENT_GREEN][:len(mn)],ax=ax4,linewidth=1.1,\n'
'            flierprops=dict(marker="o",markerfacecolor=ACCENT_RED,markersize=4,markeredgecolor=BG_COLOR))\n'
'ax4.axhline(y=80,color=ACCENT_YELLOW,linestyle="--",linewidth=1,alpha=0.7)\n'
'ax4.set_ylim(40,115); ax4.set_title("Distribusi Nilai per Komponen Praktikum",fontsize=11,fontweight="bold",pad=10,color=TEXT_COLOR)\n'
'ax4.set_xlabel("Komponen",fontsize=9); ax4.set_ylabel("Nilai",fontsize=9); ax4.grid(True,axis="y",alpha=0.4)\n'
'l4=ax4.legend(title="Mata Kuliah",loc="lower right",facecolor=PANEL_COLOR,edgecolor=GRID_COLOR,fontsize=8)\n'
'l4.get_title().set_color(TEXT_COLOR); [t.set_color(TEXT_COLOR) for t in l4.get_texts()]\n'
'\n'
'# Chart 5\n'
'ax5=fig.add_subplot(gs[1,2]); ax5.set_facecolor(CARD_COLOR)\n'
'df5s=de.sort_values("v",ascending=True)\n'
'df5s["lbl"]=df5s["nama"]+"\\n("+df5s["nama_matkul"].apply(lambda x:"".join([w[0] for w in x.split()]))+")"\n'
'nrm=df5s["v"]-df5s["v"].min(); nrm=nrm/(nrm.max()+0.01)\n'
'bc=plt.cm.plasma(0.4+nrm.values*0.5)\n'
'bars5=ax5.barh(range(len(df5s)),df5s["v"],color=bc,edgecolor=BG_COLOR,linewidth=0.8,height=0.65)\n'
'ax5.set_yticks(range(len(df5s))); ax5.set_yticklabels(df5s["lbl"].values,fontsize=7.5)\n'
'ax5.set_xlim(85,102); ax5.set_title("Top 10 Nilai Akhir Praktikum",fontsize=11,fontweight="bold",pad=10,color=TEXT_COLOR)\n'
'ax5.set_xlabel("Nilai Akhir",fontsize=9); ax5.grid(True,axis="x",alpha=0.4)\n'
'for bar,val in zip(bars5,df5s["v"]):\n'
'    ax5.text(val+0.1,bar.get_y()+bar.get_height()/2,f" {val:.2f}",va="center",ha="left",fontsize=8,color=ACCENT_YELLOW,fontweight="bold")\n'
'\n'
'# Footer\n'
'ft=fig.add_axes([0,0,1,0.018]); ft.set_facecolor("#12121C"); ft.axis("off")\n'
'ft.text(0.5,0.5,"Nathanael Komang Bagus Prakarsa  |  NIM 245091107111005  |  Sains Data - Universitas Brawijaya  |  2026",\n'
'        ha="center",va="center",fontsize=8,color="#666688")\n'
'\n'
'dash_path = os.path.join(OUTPUT_CHARTS, "dashboard_combined_anon.png")\n'
'plt.savefig(dash_path, dpi=180, bbox_inches="tight", facecolor=BG_COLOR)\n'
'plt.show()\n'
'print(f"Dashboard terpadu tersimpan: {dash_path}")\n'
))

# ── CELL 10: Summary ─────────────────────────────────────────────────
cells.append(mc(
"## ✅ Cell 10 — Ringkasan Hasil\n\n"
"| Tahap | Deskripsi | Status |\n"
"|-------|-----------|--------|\n"
"| **Skema DWH** | Star Schema: 4 dimensi + 1 tabel fakta | ✅ |\n"
"| **ETL** | Excel → Transformasi → SQLite | ✅ |\n"
"| **Anonimisasi** | 57 mahasiswa disamarkan | ✅ |\n"
"| **Query Analitik** | 6 query SQL tersimpan di `sql/dwh_queries.sql` | ✅ |\n"
"| **Visualisasi** | 5 chart premium + 1 dashboard terpadu | ✅ |\n\n"
"### Referensi:\n"
"- Kimball, R., & Ross, M. (2013). *The Data Warehouse Toolkit*. Wiley.\n"
"- McKinney, W. (2010). Data Structures for Statistical Computing in Python.\n"
"- SQLite Documentation: https://www.sqlite.org/docs.html\n"
))

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11.0"
        }
    },
    "cells": cells
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook berhasil ditulis: {OUT}")
print(f"Total cells: {len(cells)}")
