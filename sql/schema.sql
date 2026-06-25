-- ==========================================
-- PHYSICAL DESIGN - DDL SCRIPT (MYSQL)
-- ==========================================
-- Tugas Project-Based Data Warehouse Ke-II
-- Topik: Data Warehouse Nilai Akademik Mahasiswa
-- ==========================================

-- Nonaktifkan pemeriksaan foreign key untuk kelancaran reset tabel
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Hapus tabel jika sudah ada (untuk keperluan reset/re-run)
DROP TABLE IF EXISTS Fact_Nilai;
DROP TABLE IF EXISTS Dim_Mahasiswa;
DROP TABLE IF EXISTS Dim_MataKuliah;
DROP TABLE IF EXISTS Dim_KomponenNilai;
DROP TABLE IF EXISTS Dim_Periode;

-- 2. Pembuatan Tabel Dimensi: Dim_Mahasiswa
CREATE TABLE Dim_Mahasiswa (
    mahasiswa_id INT AUTO_INCREMENT PRIMARY KEY,    
    nim VARCHAR(20) NOT NULL UNIQUE,
    nama VARCHAR(150) NOT NULL,
    kelas VARCHAR(20) NOT NULL,
    angkatan INT NOT NULL
);

-- 3. Pembuatan Tabel Dimensi: Dim_MataKuliah
CREATE TABLE Dim_MataKuliah (
    matkul_id INT AUTO_INCREMENT PRIMARY KEY,   
    kode_matkul VARCHAR(20) NOT NULL UNIQUE,
    nama_matkul VARCHAR(100) NOT NULL,
    sks INT NOT NULL
);

-- 4. Pembuatan Tabel Dimensi: Dim_KomponenNilai
CREATE TABLE Dim_KomponenNilai (
    komponen_id INT AUTO_INCREMENT PRIMARY KEY,   
    nama_komponen VARCHAR(50) NOT NULL,
    bobot_persen DECIMAL(5,2) NOT NULL,
    tipe_kelas VARCHAR(20) NOT NULL CHECK (tipe_kelas IN ('praktikum', 'teori'))
);

-- 5. Pembuatan Tabel Dimensi: Dim_Periode
CREATE TABLE Dim_Periode (
    periode_id INT AUTO_INCREMENT PRIMARY KEY, 
    tahun_akademik VARCHAR(20) NOT NULL,
    semester VARCHAR(10) NOT NULL CHECK (semester IN ('Ganjil', 'Genap'))
);

-- 6. Pembuatan Tabel Fakta: Fact_Nilai
CREATE TABLE Fact_Nilai (
    nilai_id INT AUTO_INCREMENT PRIMARY KEY, 
    mahasiswa_id INT NOT NULL,
    matkul_id INT NOT NULL,
    komponen_id INT NOT NULL,
    periode_id INT NOT NULL,
    nilai_angka DECIMAL(5,2) NULL, 
    tipe_kelas VARCHAR(20) NOT NULL CHECK (tipe_kelas IN ('praktikum', 'teori')),
    status_nilai VARCHAR(30) NOT NULL CHECK (status_nilai IN ('lengkap', 'belum_dikoreksi', 'belum_dilaksanakan')),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_mahasiswa FOREIGN KEY (mahasiswa_id) REFERENCES Dim_Mahasiswa(mahasiswa_id) ON DELETE CASCADE,
    CONSTRAINT fk_matkul FOREIGN KEY (matkul_id) REFERENCES Dim_MataKuliah(matkul_id) ON DELETE CASCADE,
    CONSTRAINT fk_komponen FOREIGN KEY (komponen_id) REFERENCES Dim_KomponenNilai(komponen_id) ON DELETE CASCADE,
    CONSTRAINT fk_periode FOREIGN KEY (periode_id) REFERENCES Dim_Periode(periode_id) ON DELETE CASCADE
);

-- Aktifkan kembali pemeriksaan foreign key setelah inisialisasi skema selesai
SET FOREIGN_KEY_CHECKS = 1;

-- ==========================================
-- CATATAN PENYESUAIAN UNTUK MYSQL:
-- ==========================================
-- Jika Anda menggunakan MySQL, silakan ganti tipe data 'SERIAL PRIMARY KEY' 
-- dengan 'INT AUTO_INCREMENT PRIMARY KEY', dan hapus klausa CASCADE pada 
-- DROP TABLE (cukup DROP TABLE IF EXISTS).
-- PostgreSQL CHECK constraint didukung penuh oleh MySQL 8.0.16 ke atas.
