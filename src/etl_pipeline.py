import os
import pandas as pd
from sqlalchemy import create_engine, text

# Konfigurasi Koneksi Database MySQL
DB_URI = "mysql+mysqlconnector://root:3N4b9gs2?@localhost/dwh_nilai"
engine = create_engine(DB_URI)

def init_database_tables():
    """Membaca dan mengeksekusi file schema.sql untuk membuat tabel DWH."""
    schema_file = "schema.sql"
    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"Berkas skema {schema_file} tidak ditemukan di workspace.")
        
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_commands = f.read()
        
    # Memisahkan perintah SQL berdasarkan titik koma (;)
    commands = sql_commands.split(';')
    
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for cmd in commands:
            cmd_clean = cmd.strip()
            if cmd_clean:
                conn.execute(text(cmd_clean))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    print("Skema tabel database berhasil diinisialisasi berdasarkan schema.sql.")

def populate_metadata_dimensions():
    """Mengisi data awal untuk Dim_MataKuliah, Dim_Periode, dan Dim_KomponenNilai."""
    with engine.begin() as conn:
        # 1. Tabel Dim_MataKuliah
        conn.execute(text(
            "INSERT INTO Dim_MataKuliah (kode_matkul, nama_matkul, sks) VALUES "
            "('MAS61001', 'Metode Statistika I', 3), "
            "('MAS61002', 'Metode Statistika II', 3), "
            "('MSD61001', 'Metode Sains Data I', 3) "
            "ON DUPLICATE KEY UPDATE nama_matkul=VALUES(nama_matkul), sks=VALUES(sks);"
        ))
        
        # 2. Tabel Dim_Periode
        conn.execute(text(
            "INSERT INTO Dim_Periode (tahun_akademik, semester) VALUES "
            "('2025/2026', 'Ganjil'), "
            "('2025/2026', 'Genap') "
            "ON DUPLICATE KEY UPDATE tahun_akademik=VALUES(tahun_akademik);"
        ))
        
        # 3. Tabel Dim_KomponenNilai
        # Pembobotan praktikum sesuai formula asli kartu kendali:
        # Tugas 1 (15%), Tugas 2 (15%), Presensi (15%), Sikap (5%), UTP/Quis (20%), UAP/Ujian (30%)
        # Pembobotan teori kelas MS2: Kuis 1 (10%), Kuis 2 (10%), UTS (40%), UAS (40%)
        conn.execute(text(
            "INSERT INTO Dim_KomponenNilai (nama_komponen, bobot_persen, tipe_kelas) VALUES "
            "('Tugas 1', 15.0, 'praktikum'), "
            "('Tugas 2', 15.0, 'praktikum'), "
            "('Presensi', 15.0, 'praktikum'), "
            "('Sikap', 5.0, 'praktikum'), "
            "('UTP', 20.0, 'praktikum'), "
            "('UAP', 30.0, 'praktikum'), "
            "('Kuis 1', 10.0, 'teori'), "
            "('Kuis 2', 10.0, 'teori'), "
            "('UTS', 40.0, 'teori'), "
            "('UAS', 40.0, 'teori') "
            "ON DUPLICATE KEY UPDATE bobot_persen=VALUES(bobot_persen);"
        ))
    print("Metadata dimensi akademik berhasil dimuat.")

def run_etl_pipeline():
    """Proses utama ETL: ekstraksi data Excel, transformasi, dan pemuatan ke database."""
    # Sumber Data Transaksional (Excel)
    prac_files = {
        "MSD1": ("Presensi Kegiatan Praktikum MK Metode Sains Data I Kelas SA1 (PSS Sains Data).xlsx", "Genap", "MSD61001"),
        "MS1": ("Presensi Kegiatan Praktikum MK Metode Statistika I Kelas SA1 (PSS Sains Data).xlsx", "Ganjil", "MAS61001"),
        "MS2": ("Presensi Kegiatan Praktikum MK Metode Statistika II Kelas SA1 (PSS Sains Data).xlsx", "Genap", "MAS61002")
    }
    theory_file = "Nilai Metode Statistika II PS Sains Data 2026.xlsx"
    
    # ----------------------------------------------------
    # PHASE 1: EXTRACT & TRANSFORM (Mahasiswa Dimension)
    # ----------------------------------------------------
    students_registry = {}
    
    # Ekstraksi mahasiswa dari seluruh file praktikum
    for name, (file, _, _) in prac_files.items():
        if os.path.exists(file):
            df = pd.read_excel(file, sheet_name='Penilaian', header=None)
            for idx, row in df.iloc[14:].iterrows():
                nim = row[5]
                nama = row[1]
                if pd.notna(nim) and str(nim).strip().isdigit():
                    nim_str = str(int(nim)).strip()
                    nama_str = str(nama).strip().upper()
                    angkatan = int("20" + nim_str[:2]) if len(nim_str) >= 2 else 2025
                    students_registry[nim_str] = {
                        "nama": nama_str,
                        "kelas": "SA1",
                        "angkatan": angkatan
                    }
                    
    # Ekstraksi mahasiswa dari kelas teori MS2
    if os.path.exists(theory_file):
        xl = pd.ExcelFile(theory_file)
        df_t = xl.parse('KUIS 1', header=None)
        for idx, row in df_t.iloc[2:].iterrows():
            nim = row[3]
            nama = row[2]
            if pd.notna(nim) and str(nim).strip().isdigit():
                nim_str = str(int(nim)).strip()
                nama_str = str(nama).strip().upper()
                angkatan = int("20" + nim_str[:2]) if len(nim_str) >= 2 else 2025
                if nim_str not in students_registry:
                    students_registry[nim_str] = {
                        "nama": nama_str,
                        "kelas": "Teori-A",
                        "angkatan": angkatan
                    }

    # Muat dimensi Dim_Mahasiswa
    mahasiswa_id_map = {}
    with engine.begin() as conn:
        for nim_str, info in students_registry.items():
            conn.execute(
                text("INSERT INTO Dim_Mahasiswa (nim, nama, kelas, angkatan) VALUES (:nim, :nama, :kelas, :angkatan) "
                     "ON DUPLICATE KEY UPDATE nama=VALUES(nama), kelas=VALUES(kelas);"),
                {"nim": nim_str, "nama": info["nama"], "kelas": info["kelas"], "angkatan": info["angkatan"]}
            )
        
        # Mapping kembali ID dari database
        result = conn.execute(text("SELECT mahasiswa_id, nim FROM Dim_Mahasiswa"))
        for row in result:
            mahasiswa_id_map[row[1]] = row[0]
            
        # Membaca metadata pemetaan lainnya
        matkul_map = {row[1]: row[0] for row in conn.execute(text("SELECT matkul_id, kode_matkul FROM Dim_MataKuliah"))}
        periode_map = {(row[1], row[2]): row[0] for row in conn.execute(text("SELECT periode_id, tahun_akademik, semester FROM Dim_Periode"))}
        komponen_map = {(row[1], row[2]): row[0] for row in conn.execute(text("SELECT komponen_id, nama_komponen, tipe_kelas FROM Dim_KomponenNilai"))}

    # ----------------------------------------------------
    # PHASE 2: EXTRACT & TRANSFORM (Fact Table - Nilai)
    # ----------------------------------------------------
    facts_buffer = []
    
    # 2.1 Pemrosesan Kelas Praktikum
    prac_columns_map = {
        "Tugas 1": 6,
        "Tugas 2": 7,
        "Presensi": 8,
        "Sikap": 9,
        "UTP": 10,  # Berasal dari kolom 'Quis'
        "UAP": 11   # Berasal dari kolom 'Ujian'
    }
    
    for name, (file, semester, kode_matkul) in prac_files.items():
        if not os.path.exists(file):
            continue
        df = pd.read_excel(file, sheet_name='Penilaian', header=None)
        matkul_id = matkul_map[kode_matkul]
        periode_id = periode_map[("2025/2026", semester)]
        
        for idx, row in df.iloc[14:].iterrows():
            nim = row[5]
            if pd.notna(nim) and str(nim).strip().isdigit():
                nim_str = str(int(nim)).strip()
                mahasiswa_id = mahasiswa_id_map[nim_str]
                
                for comp_name, col_idx in prac_columns_map.items():
                    val = row[col_idx]
                    komponen_id = komponen_map[(comp_name, "praktikum")]
                    
                    score = None
                    status = 'lengkap'
                    
                    # Konversi nilai ke float, lewati jika anomali pembagian nol atau kosong
                    if pd.notna(val) and str(val).strip() != "" and str(val).strip() != '#DIV/0!':
                        try:
                            score = float(val)
                        except ValueError:
                            score = None
                            
                    # Tentukan status berdasarkan karakteristik kemajuan kelas praktikum
                    if score is None:
                        if name == "MS1":
                            status = 'lengkap'  # MS1 praktikum sudah dinilai penuh
                        elif name == "MS2":
                            # MS2 praktikum belum diinput Tugas 2 dan UAP
                            status = 'belum_dikoreksi' if comp_name in ["Tugas 2", "UAP"] else 'lengkap'
                        elif name == "MSD1":
                            # MSD1 praktikum baru diinput nilai UAP
                            status = 'lengkap' if comp_name == "UAP" else 'belum_dikoreksi'
                    else:
                        status = 'lengkap'
                        
                    facts_buffer.append({
                        "mahasiswa_id": mahasiswa_id,
                        "matkul_id": matkul_id,
                        "komponen_id": komponen_id,
                        "periode_id": periode_id,
                        "nilai_angka": score,
                        "tipe_kelas": "praktikum",
                        "status_nilai": status
                    })

    # 2.2 Pemrosesan Kelas Teori
    theory_sheets = {
        "Kuis 1": ("Kuis 1", "KUIS 1", 8),
        "Kuis 2": ("Kuis 2", "KUIS 2", 10),
        "UTS": ("UTS", "UTS", 11),
        "UAS": ("UAS", "UAS", 11)
    }
    
    if os.path.exists(theory_file):
        xl = pd.ExcelFile(theory_file)
        matkul_id = matkul_map["MAS61002"]
        periode_id = periode_map[("2025/2026", "Genap")]
        
        for comp_name, (comp_key, sheet_name, col_idx) in theory_sheets.items():
            df = xl.parse(sheet_name, header=None)
            komponen_id = komponen_map[(comp_name, "teori")]
            
            for idx, row in df.iloc[2:].iterrows():
                nim = row[3]
                if pd.notna(nim) and str(nim).strip().isdigit():
                    nim_str = str(int(nim)).strip()
                    mahasiswa_id = mahasiswa_id_map[nim_str]
                    
                    # Cek kolom sub-soal untuk verifikasi ujian telah berlangsung
                    if comp_name == "Kuis 1":
                        sub_cols = row[4:8]
                    elif comp_name == "Kuis 2":
                        sub_cols = row[4:10]
                    else:
                        sub_cols = row[4:11]
                        
                    is_all_nan = sub_cols.isna().all()
                    val = row[col_idx]
                    score = None
                    status = 'lengkap'
                    
                    if not is_all_nan and pd.notna(val) and str(val).strip() != "" and str(val).strip() != '#DIV/0!':
                        try:
                            score = float(val)
                            status = 'lengkap'
                        except ValueError:
                            score = None
                            
                    # Penentuan status untuk kelas teori
                    if score is None or is_all_nan:
                        score = None
                        # UAS belum dilaksanakan sama sekali, Kuis 2 Rachel terlewat koreksi/absen
                        status = 'belum_dilaksanakan' if comp_name == "UAS" else 'belum_dikoreksi'
                        
                    facts_buffer.append({
                        "mahasiswa_id": mahasiswa_id,
                        "matkul_id": matkul_id,
                        "komponen_id": komponen_id,
                        "periode_id": periode_id,
                        "nilai_angka": score,
                        "tipe_kelas": "teori",
                        "status_nilai": status
                    })

    # ----------------------------------------------------
    # PHASE 3: LOAD (Fact Table - Nilai)
    # ----------------------------------------------------
    with engine.begin() as conn:
        # Menghapus data fakta lama untuk re-run yang bersih
        conn.execute(text("TRUNCATE TABLE Fact_Nilai;"))
        
        # Bulk insert
        for fact in facts_buffer:
            conn.execute(
                text("INSERT INTO Fact_Nilai (mahasiswa_id, matkul_id, komponen_id, periode_id, nilai_angka, tipe_kelas, status_nilai) "
                     "VALUES (:mahasiswa_id, :matkul_id, :komponen_id, :periode_id, :nilai_angka, :tipe_kelas, :status_nilai)"),
                fact
            )
            
    print(f"ETL sukses! Total {len(facts_buffer)} baris fakta nilai berhasil dimuat ke Fact_Nilai.")

if __name__ == "__main__":
    print("=== MEMULAI PIPELINE ETL DATA WAREHOUSE ===")
    init_database_tables()
    populate_metadata_dimensions()
    run_etl_pipeline()
    print("=== PIPELINE ETL SELESAI DENGAN SUKSES ===")
