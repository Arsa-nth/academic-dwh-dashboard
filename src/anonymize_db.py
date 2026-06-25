"""
Script Anonimisasi Data Mahasiswa
==================================
Membuat salinan database (dwh_nilai_anon.db) dengan nama mahasiswa
dan NIM yang sudah disamarkan untuk keperluan portfolio publik.

Nama asli -> "Mahasiswa 01", "Mahasiswa 02", dst.
NIM asli  -> "STD2500001", "STD2500002", dst.
"""

import sqlite3
import shutil
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DB   = os.path.join(BASE_DIR, "data", "dwh_nilai.db")
DST_DB   = os.path.join(BASE_DIR, "data", "dwh_nilai_anon.db")

def anonymize():
    # Salin database asli
    shutil.copy2(SRC_DB, DST_DB)
    print(f"Database disalin ke: {DST_DB}")

    conn = sqlite3.connect(DST_DB)
    cur  = conn.cursor()

    # Ambil semua mahasiswa, urutkan konsisten
    cur.execute("SELECT mahasiswa_id, nim, nama FROM Dim_Mahasiswa ORDER BY mahasiswa_id")
    rows = cur.fetchall()

    print(f"Total mahasiswa ditemukan: {len(rows)}")

    for idx, (mhs_id, nim_asli, nama_asli) in enumerate(rows, start=1):
        fake_nama = f"Mahasiswa {idx:02d}"
        fake_nim  = f"STD2500{idx:03d}"
        cur.execute(
            "UPDATE Dim_Mahasiswa SET nama=?, nim=? WHERE mahasiswa_id=?",
            (fake_nama, fake_nim, mhs_id)
        )
        print(f"  [{idx:02d}] {nama_asli[:30]:<30} -> {fake_nama}  |  {nim_asli} -> {fake_nim}")

    conn.commit()
    conn.close()
    print("\n✅ Anonimisasi selesai! Database anonim tersimpan di:", DST_DB)

if __name__ == "__main__":
    anonymize()
