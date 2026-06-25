import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set standard design aesthetics for premium dark mode
plt.style.use('dark_background')
sns.set_theme(style="dark", palette="muted")

# Custom HSL-like sleek dark mode color palette
BG_COLOR = '#121214'       # Very dark charcoal
CARD_COLOR = '#1E1E24'     # Dark gray for card-like container
TEXT_COLOR = '#E4E4E7'     # Off-white
ACCENT_BLUE = '#3B82F6'    # Neon Cyan/Blue
ACCENT_PURPLE = '#8B5CF6'  # Neon Purple
ACCENT_GREEN = '#10B981'   # Neon Green
ACCENT_YELLOW = '#F59E0B'  # Amber Gold
ACCENT_RED = '#EF4444'     # Neon Red

plt.rcParams.update({
    'figure.facecolor': BG_COLOR,
    'axes.facecolor': CARD_COLOR,
    'text.color': TEXT_COLOR,
    'axes.labelcolor': TEXT_COLOR,
    'xtick.color': TEXT_COLOR,
    'ytick.color': TEXT_COLOR,
    'font.family': 'sans-serif',
    'grid.color': '#2D2D30',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'axes.edgecolor': '#2D2D30'
})

# Connect to database
conn = sqlite3.connect('dwh_nilai.db')

def draw_chart_1():
    """Chart 1: Progress Kelengkapan Data per Tipe Kelas (Stacked Bar Chart)"""
    query = """
        SELECT 
            tipe_kelas,
            status_nilai,
            COUNT(*) AS jumlah_record
        FROM Fact_Nilai
        GROUP BY tipe_kelas, status_nilai;
    """
    df = pd.read_sql_query(query, conn)
    
    # Pivot to get stacked representation
    df_pivot = df.pivot(index='tipe_kelas', columns='status_nilai', values='jumlah_record').fillna(0)
    
    # Standardize column order if exists
    for col in ['lengkap', 'belum_dikoreksi', 'belum_dilaksanakan']:
        if col not in df_pivot.columns:
            df_pivot[col] = 0
            
    df_pivot = df_pivot[['lengkap', 'belum_dikoreksi', 'belum_dilaksanakan']]
    
    # Calculate percentage
    df_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(8, 5))
    df_pct.plot(kind='barh', stacked=True, color=[ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED], ax=ax, edgecolor=BG_COLOR, width=0.5)
    
    ax.set_title("Progress Kelengkapan Data Nilai per Tipe Kelas (%)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Persentase (%)", fontsize=12)
    ax.set_ylabel("Tipe Kelas", fontsize=12)
    ax.set_xlim(0, 100)
    
    # Customize Legend
    legend = ax.legend(title="Status Nilai", bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, facecolor=CARD_COLOR, edgecolor='#2D2D30')
    legend.get_title().set_color(TEXT_COLOR)
    
    # Add values on bars
    for p in ax.patches:
        width = p.get_width()
        if width > 5:  # only label segments larger than 5%
            ax.annotate(f"{width:.1f}%", 
                        (p.get_x() + width/2, p.get_y() + p.get_height()/2),
                        ha='center', va='center', color='#FFFFFF', fontsize=10, fontweight='bold')
            
    plt.tight_layout()
    plt.savefig('chart1_progress.png', dpi=300, facecolor=BG_COLOR)
    plt.close()
    print("Chart 1 generated!")

def draw_chart_2():
    """Chart 2: Perbandingan Performa Kelas Teori vs Praktikum (Violin/Box Plot)"""
    query = """
        SELECT tipe_kelas, nilai_angka 
        FROM Fact_Nilai 
        WHERE status_nilai = 'lengkap';
    """
    df = pd.read_sql_query(query, conn)
    
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Premium styled violin plot combined with box plot
    sns.violinplot(x='tipe_kelas', y='nilai_angka', data=df, inner='box', palette=[ACCENT_BLUE, ACCENT_PURPLE], ax=ax, linewidth=1.5)
    
    ax.set_title("Perbandingan Performa Nilai: Teori vs Praktikum", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Tipe Kelas", fontsize=12)
    ax.set_ylabel("Nilai Angka", fontsize=12)
    ax.grid(True)
    
    # Annotate averages
    means = df.groupby('tipe_kelas')['nilai_angka'].mean()
    for i, tipe in enumerate(means.index):
        ax.annotate(f"Rata-rata: {means[tipe]:.2f}", 
                    xy=(i, means[tipe]), 
                    xytext=(i - 0.2, means[tipe] + 8),
                    color='#FFFFFF', weight='bold', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", fc=CARD_COLOR, ec=ACCENT_YELLOW, lw=1))
        
    plt.tight_layout()
    plt.savefig('chart2_teori_vs_praktikum.png', dpi=300, facecolor=BG_COLOR)
    plt.close()
    print("Chart 2 generated!")

def draw_chart_3():
    """Chart 3: Rata-rata Nilai per Mata Kuliah & Tipe Kelas (Grouped Bar Chart)"""
    query = """
        SELECT 
            m.nama_matkul,
            f.tipe_kelas,
            AVG(f.nilai_angka) AS rata_rata_nilai
        FROM Fact_Nilai f
        JOIN Dim_MataKuliah m ON f.matkul_id = m.matkul_id
        WHERE f.status_nilai = 'lengkap'
        GROUP BY m.nama_matkul, f.tipe_kelas;
    """
    df = pd.read_sql_query(query, conn)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.barplot(x='nama_matkul', y='rata_rata_nilai', hue='tipe_kelas', data=df, 
                palette=[ACCENT_BLUE, ACCENT_PURPLE], ax=ax, edgecolor='#2D2D30', width=0.6)
    
    ax.set_title("Perbandingan Rata-rata Nilai per Mata Kuliah", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Mata Kuliah", fontsize=12)
    ax.set_ylabel("Rata-rata Nilai", fontsize=12)
    ax.set_ylim(0, 110)
    ax.grid(True)
    
    # Add value labels
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f"{height:.2f}",
                        (p.get_x() + p.get_width()/2., height + 2),
                        ha='center', va='center', color=TEXT_COLOR, fontsize=10, fontweight='bold')
            
    legend = ax.legend(title="Tipe Kelas", facecolor=CARD_COLOR, edgecolor='#2D2D30')
    legend.get_title().set_color(TEXT_COLOR)
    
    plt.tight_layout()
    plt.savefig('chart3_performa_matkul.png', dpi=300, facecolor=BG_COLOR)
    plt.close()
    print("Chart 3 generated!")

def draw_chart_4():
    """Chart 4: Distribusi Nilai per Komponen per Mata Kuliah (Box Plots)"""
    query = """
        SELECT 
            m.nama_matkul,
            k.nama_komponen,
            f.nilai_angka
        FROM Fact_Nilai f
        JOIN Dim_MataKuliah m ON f.matkul_id = m.matkul_id
        JOIN Dim_KomponenNilai k ON f.komponen_id = k.komponen_id
        WHERE f.status_nilai = 'lengkap' AND f.tipe_kelas = 'praktikum';
    """
    df = pd.read_sql_query(query, conn)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    sns.boxplot(x='nama_komponen', y='nilai_angka', hue='nama_matkul', data=df, 
                palette='viridis', ax=ax, linewidth=1.2, flierprops=dict(marker='o', markerfacecolor=ACCENT_RED, markersize=5))
    
    ax.set_title("Distribusi Nilai per Komponen Kelas Praktikum", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Komponen Nilai", fontsize=12)
    ax.set_ylabel("Nilai Mahasiswa", fontsize=12)
    ax.grid(True)
    
    legend = ax.legend(title="Mata Kuliah", bbox_to_anchor=(1.01, 1), loc='upper left', facecolor=CARD_COLOR, edgecolor='#2D2D30')
    legend.get_title().set_color(TEXT_COLOR)
    
    plt.tight_layout()
    plt.savefig('chart4_distribusi_komponen.png', dpi=300, facecolor=BG_COLOR)
    plt.close()
    print("Chart 4 generated!")

def draw_chart_5():
    """Chart 5: Peringkat Nilai Akhir Praktikum Mahasiswa (Top 10)"""
    query = """
        SELECT 
            m.nama AS nama_mahasiswa,
            mk.nama_matkul,
            ROUND(SUM(f.nilai_angka * (k.bobot_persen / 100.0)), 2) AS nilai_akhir
        FROM Fact_Nilai f
        JOIN Dim_Mahasiswa m ON f.mahasiswa_id = m.mahasiswa_id
        JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id
        JOIN Dim_KomponenNilai k ON f.komponen_id = k.komponen_id
        WHERE f.tipe_kelas = 'praktikum' AND f.nilai_angka IS NOT NULL
        GROUP BY m.nim, m.nama, mk.nama_matkul
        ORDER BY nilai_akhir DESC
        LIMIT 10;
    """
    df = pd.read_sql_query(query, conn)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    # Create labels with student name + course name
    df['label'] = df['nama_mahasiswa'] + "\n(" + df['nama_matkul'].apply(lambda x: "".join([w[0] for w in x.split()])) + ")"
    
    sns.barplot(x='nilai_akhir', y='label', data=df, palette='plasma', ax=ax, edgecolor='#2D2D30', width=0.6)
    
    ax.set_title("Peringkat Nilai Akhir Praktikum (Top 10 Mahasiswa)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Nilai Akhir Estimasi", fontsize=12)
    ax.set_ylabel("Nama Mahasiswa & Matkul", fontsize=12)
    ax.set_xlim(85, 101)  # Focus on the high score range
    ax.grid(True)
    
    # Add values on the right of bars
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f" {width:.2f}",
                    (width, p.get_y() + p.get_height()/2.),
                    ha='left', va='center', color=TEXT_COLOR, fontsize=10, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('chart5_top_students.png', dpi=300, facecolor=BG_COLOR)
    plt.close()
    print("Chart 5 generated!")

if __name__ == "__main__":
    draw_chart_1()
    draw_chart_2()
    draw_chart_3()
    draw_chart_4()
    draw_chart_5()
    print("All premium dashboard charts generated successfully!")
    conn.close()
