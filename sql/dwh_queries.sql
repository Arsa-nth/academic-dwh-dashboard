-- ==========================================
-- DWH ANALITIK QUERIES
-- ==========================================
-- Project: Data Warehouse Nilai Akademik Mahasiswa
-- Program Studi Sains Data - Universitas Brawijaya
-- T.A. 2025/2026
-- Note: Data mahasiswa telah dianonimkan (nama & NIM)
-- ==========================================

-- ------------------------------------------
-- Q1: Progress Kelengkapan Data per Tipe Kelas
-- ------------------------------------------
-- Menghitung persentase status nilai (lengkap, belum dikoreksi,
-- belum dilaksanakan) dikelompokkan per tipe kelas.
SELECT
    tipe_kelas,
    status_nilai,
    COUNT(*)                                        AS jumlah_record,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER
          (PARTITION BY tipe_kelas), 2)             AS persen
FROM Fact_Nilai
GROUP BY tipe_kelas, status_nilai
ORDER BY tipe_kelas, status_nilai;


-- ------------------------------------------
-- Q2: Distribusi Nilai Teori vs Praktikum
-- ------------------------------------------
-- Statistik deskriptif (min, max, rata-rata, median-proxy)
-- untuk masing-masing tipe kelas.
SELECT
    tipe_kelas,
    COUNT(nilai_angka)                              AS n_nilai,
    ROUND(MIN(nilai_angka), 2)                      AS nilai_min,
    ROUND(MAX(nilai_angka), 2)                      AS nilai_max,
    ROUND(AVG(nilai_angka), 2)                      AS rata_rata,
    ROUND(AVG(nilai_angka * nilai_angka) -
          AVG(nilai_angka) * AVG(nilai_angka), 2)   AS variansi
FROM Fact_Nilai
WHERE status_nilai = 'lengkap'
GROUP BY tipe_kelas;


-- ------------------------------------------
-- Q3: Rata-rata Nilai per Mata Kuliah & Tipe Kelas
-- ------------------------------------------
SELECT
    mk.kode_matkul,
    mk.nama_matkul,
    f.tipe_kelas,
    COUNT(DISTINCT f.mahasiswa_id)                  AS jumlah_mahasiswa,
    ROUND(AVG(f.nilai_angka), 2)                    AS rata_rata_nilai,
    ROUND(MIN(f.nilai_angka), 2)                    AS nilai_min,
    ROUND(MAX(f.nilai_angka), 2)                    AS nilai_max
FROM Fact_Nilai f
JOIN Dim_MataKuliah mk ON f.matkul_id = mk.matkul_id
WHERE f.status_nilai = 'lengkap'
GROUP BY mk.matkul_id, f.tipe_kelas
ORDER BY mk.kode_matkul, f.tipe_kelas;


-- ------------------------------------------
-- Q4: Distribusi Nilai per Komponen (Praktikum)
-- ------------------------------------------
SELECT
    mk.nama_matkul,
    k.nama_komponen,
    k.bobot_persen,
    COUNT(f.nilai_angka)                            AS n_mahasiswa,
    ROUND(AVG(f.nilai_angka), 2)                    AS rata_rata,
    ROUND(MIN(f.nilai_angka), 2)                    AS nilai_min,
    ROUND(MAX(f.nilai_angka), 2)                    AS nilai_max
FROM Fact_Nilai f
JOIN Dim_MataKuliah mk ON f.matkul_id  = mk.matkul_id
JOIN Dim_KomponenNilai k ON f.komponen_id = k.komponen_id
WHERE f.status_nilai = 'lengkap'
  AND f.tipe_kelas   = 'praktikum'
GROUP BY mk.matkul_id, k.komponen_id
ORDER BY mk.nama_matkul, k.bobot_persen DESC;


-- ------------------------------------------
-- Q5: Peringkat Nilai Akhir Praktikum (Top 10)
-- ------------------------------------------
-- Nilai akhir dihitung sebagai rata-rata tertimbang
-- komponen * bobot masing-masing.
SELECT
    m.nim                                           AS id_mahasiswa,
    m.nama                                          AS nama_mahasiswa,
    mk.nama_matkul,
    ROUND(SUM(f.nilai_angka * (k.bobot_persen / 100.0)), 2) AS nilai_akhir_estimasi
FROM Fact_Nilai f
JOIN Dim_Mahasiswa    m  ON f.mahasiswa_id = m.mahasiswa_id
JOIN Dim_MataKuliah   mk ON f.matkul_id    = mk.matkul_id
JOIN Dim_KomponenNilai k ON f.komponen_id  = k.komponen_id
WHERE f.tipe_kelas    = 'praktikum'
  AND f.nilai_angka IS NOT NULL
GROUP BY m.mahasiswa_id, mk.matkul_id
ORDER BY nilai_akhir_estimasi DESC
LIMIT 10;


-- ------------------------------------------
-- Q6: Summary KPI Keseluruhan (Metric Cards)
-- ------------------------------------------
SELECT
    (SELECT COUNT(DISTINCT mahasiswa_id)
     FROM   Dim_Mahasiswa)                          AS total_mahasiswa,
    (SELECT COUNT(*)
     FROM   Fact_Nilai)                             AS total_records,
    (SELECT COUNT(*)
     FROM   Fact_Nilai WHERE status_nilai = 'lengkap') AS total_lengkap,
    (SELECT ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Fact_Nilai), 1)
     FROM   Fact_Nilai WHERE status_nilai = 'lengkap') AS pct_lengkap,
    (SELECT ROUND(AVG(nilai_angka), 2)
     FROM   Fact_Nilai WHERE status_nilai = 'lengkap') AS avg_nilai_overall,
    (SELECT ROUND(AVG(nilai_angka), 2)
     FROM   Fact_Nilai WHERE status_nilai = 'lengkap'
       AND  tipe_kelas = 'praktikum')               AS avg_nilai_praktikum,
    (SELECT ROUND(AVG(nilai_angka), 2)
     FROM   Fact_Nilai WHERE status_nilai = 'lengkap'
       AND  tipe_kelas = 'teori')                   AS avg_nilai_teori,
    (SELECT COUNT(DISTINCT matkul_id)
     FROM   Dim_MataKuliah)                         AS total_matkul;
