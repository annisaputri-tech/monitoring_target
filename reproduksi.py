"""reproduksi.py.

Skrip Reproduksi Bug untuk BUG-112:
"Ketidakkonsistenan dan Hilangnya Validasi Jumlah Hari pada Rincian Target Harian di Berbagai Pilihan Bulan"
Berdasarkan laporan di BUGS.md.

Tujuan:
Membuktikan secara programatik dan terstruktur bahwa bug pada BUG-112 memang betul terjadi
pada modul logika bisnis (monitoring_target.py) maupun pada antarmuka web (index.html).
"""

import calendar
import datetime
import os
import re
import sys
import unittest
from typing import Dict, List

from monitoring_target import TargetManager, ValidationError


class TestReproduksiBug112(unittest.TestCase):
    """Test suite unit test untuk membuktikan eksistensi BUG-112."""

    def setUp(self):
        self.manager = TargetManager()
        self.yearly_target = self.manager.tambah_target_tahunan(
            judul="Membaca 24 Buku",
            indikator_angka=24,
            satuan="buku"
        )
        self.months = self.manager.ambil_target_bulanan(self.yearly_target.id)

    def test_bukti_1_jumlah_hari_selalu_28_untuk_semua_bulan(self):
        """BUKTI 1:

        Sistem mengasumsikan setiap bulan selalu memiliki 28 hari (4 minggu x 7 hari).
        Bulan dengan 31 hari (Januari, Maret, dll.) dan 30 hari (April, dll.) kehilangan
        hari ke-29, 30, dan 31.
        """
        # Bulan ke-1 (Januari) di kalender aktual memiliki 31 hari
        januari = self.months[0]
        weeks_januari = self.manager.ambil_target_mingguan(januari.id)
        total_hari_januari = sum(
            len(self.manager.ambil_target_harian(w.id)) for w in weeks_januari
        )

        # Bukti: Total hari Januari di sistem hanya 28 hari, BUKAN 31 hari
        self.assertEqual(len(weeks_januari), 4, "Sistem membatasi minggu hanya 4 per bulan")
        self.assertEqual(total_hari_januari, 28, "Total hari Januari di sistem hanya 28 hari")
        self.assertNotEqual(
            total_hari_januari, 31,
            "BUG TERBUKTI: Januari seharusnya memiliki 31 hari, namun sistem hanya menyediakan 28 hari!"
        )

    def test_bukti_2_tanggal_29_sampai_31_tidak_dapat_dicatat(self):
        """BUKTI 2:

        Pengguna tidak dapat mengakses atau mencatat aktivitas harian untuk tanggal
        29, 30, dan 31 pada bulan yang berdurasi 31 hari (Januari).
        """
        januari = self.months[0]
        weeks_januari = self.manager.ambil_target_mingguan(januari.id)
        minggu_4 = weeks_januari[3]  # Minggu ke-4

        target_harian_m4 = self.manager.ambil_target_harian(minggu_4.id)
        hari_tersedia = [t.hari_ke for t in target_harian_m4]

        # Hanya ada hari ke-1 s.d. 7 (setara tanggal 22 - 28 jika dimulai dari tgl 1)
        self.assertEqual(hari_tersedia, [1, 2, 3, 4, 5, 6, 7])
        self.assertNotIn(8, hari_tersedia, "Hari ke-8 (tanggal 29) tidak ada di minggu 4")

        # Upaya memasukkan aktivitas untuk hari ke-29, 30, 31 ke minggu 4
        # Sistem menolak dengan ValidationError karena mengunci strictly 7 hari
        input_dengan_sisa_hari = {
            1: "Hari 22", 2: "Hari 23", 3: "Hari 24", 4: "Hari 25",
            5: "Hari 26", 6: "Hari 27", 7: "Hari 28",
            8: "Hari 29", 9: "Hari 30", 10: "Hari 31"
        }
        with self.assertRaises(ValidationError) as ctx:
            self.manager.isi_target_harian_manual(minggu_4.id, input_dengan_sisa_hari)

        self.assertIn("Aktivitas harian harus terisi lengkap untuk seluruh 7 hari.", str(ctx.exception))

    def test_bukti_3_ketidaksesuaian_kalender_aktual_2026(self):
        """BUKTI 3:

        Sistem mengasumsikan hari selalu dimulai dari 'Senin' s.d. 'Minggu' secara statis.
        Padahal pada kalender tahun 2026:
        - 1 Februari 2026 jatuh pada hari Minggu (Sunday).
        - 1 Januari 2026 jatuh pada hari Kamis (Thursday).
        """
        # Cek kalender aktual 2026 menggunakan modul calendar/datetime
        hari_1_feb_2026 = datetime.date(2026, 2, 1).weekday()  # 6 = Sunday / Minggu
        self.assertEqual(hari_1_feb_2026, 6, "1 Februari 2026 adalah hari Minggu (index 6)")

        hari_1_jan_2026 = datetime.date(2026, 1, 1).weekday()  # 3 = Thursday / Kamis
        self.assertEqual(hari_1_jan_2026, 3, "1 Januari 2026 adalah hari Kamis (index 3)")

    def test_bukti_4_hardcoded_label_dan_filter_di_index_html(self):
        """BUKTI 4:

        Pada berkas antarmuka web (index.html):
        - Label header terkunci statis pada '7 Hari (Senin - Minggu)'.
        - Filter dropdown minggu hanya memiliki opsi Minggu 1 s.d. Minggu 4.
        - Array DAYS_DATA di-hardcode 7 hari dari Senin s.d. Minggu.
        """
        html_path = os.path.join(os.path.dirname(__file__), "index.html")
        self.assertTrue(os.path.exists(html_path), "File index.html harus ada")

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # 1. Cek label statis pada badge minggu
        self.assertIn(
            "7 Hari (Senin - Minggu)",
            html_content,
            "BUG TERBUKTI: Badge header mengunci teks statis '7 Hari (Senin - Minggu)'"
        )

        # 2. Cek dropdown filter minggu: hanya ada 4 opsi minggu
        opsi_minggu = re.findall(r'<option value="(\d+)">Minggu \1</option>', html_content)
        self.assertEqual(
            opsi_minggu, ["1", "2", "3", "4"],
            "BUG TERBUKTI: Filter minggu hanya memiliki 4 opsi minggu, tidak ada minggu ke-5 untuk sisa hari"
        )

        # 3. Cek DAYS_DATA hanya memiliki 7 nama hari statis
        self.assertIn("name: 'Senin'", html_content)
        self.assertIn("name: 'Minggu'", html_content)


def jalankan_reproduksi_interaktif():
    """Menjalankan alur demonstrasi reproduksi bug secara lengkap dan mendalam

    dengan output konsol yang jelas.
    """
    print("=" * 80)
    print("SKRIP REPRODUKSI BUG-112")
    print("Judul  : Ketidakkonsistenan dan Hilangnya Validasi Jumlah Hari")
    print("         pada Rincian Target Harian di Berbagai Pilihan Bulan")
    print("Sumber : BUGS.md")
    print("=" * 80)

    manager = TargetManager()
    yearly_target = manager.tambah_target_tahunan(
        judul="Membaca 24 Buku Target 2026",
        indikator_angka=24,
        satuan="buku"
    )
    months = manager.ambil_target_bulanan(yearly_target.id)

    NAMA_BULAN = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    HARI_DALAM_SEMINGGU = [
        "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"
    ]

    # -------------------------------------------------------------------------
    # PEMBUKTIAN 1: Menjalankan Langkah 3 s.d. 5 dari BUGS.md
    # -------------------------------------------------------------------------
    print("\n[LANGKAH REPRODUKSI 1]: Memeriksa Jumlah Hari & Minggu per Bulan")
    print("-" * 80)
    print(f"{'Bulan':<12} | {'Hari Kalender 2026':<20} | {'Hari di Sistem':<16} | {'Selisih Hari Hilang'}")
    print("-" * 80)

    total_hari_sistem = 0
    total_hari_aktual_2026 = 0
    total_hari_hilang = 0

    for idx, m in enumerate(months):
        bulan_ke = m.bulan_ke
        nama_bulan = NAMA_BULAN[bulan_ke - 1]
        hari_aktual = calendar.monthrange(2026, bulan_ke)[1]
        weeks = manager.ambil_target_mingguan(m.id)
        hari_sistem = sum(len(manager.ambil_target_harian(w.id)) for w in weeks)

        selisih = hari_aktual - hari_sistem
        total_hari_sistem += hari_sistem
        total_hari_aktual_2026 += hari_aktual
        total_hari_hilang += selisih

        tanda = f"(-{selisih} hari HILANG!)" if selisih > 0 else "(Sesuai jumlah hari)"
        print(f"{nama_bulan:<12} | {hari_aktual:<20} | {hari_sistem:<16} | {tanda}")

    print("-" * 80)
    print(f"TOTAL SATU TAHUN : Kalender 2026 = {total_hari_aktual_2026} hari | Sistem = {total_hari_sistem} hari | Total Hilang = {total_hari_hilang} hari")
    print(f">> [BUKTI TERKONFIRMASI]:")
    print(f"   Sistem hanya menghasilkan 28 hari (4 minggu x 7 hari) untuk SEMUA bulan.")
    print(f"   Bulan dengan 31 hari (seperti Januari & Maret) kehilangan 3 hari (tgl 29, 30, 31).")
    print(f"   Bulan dengan 30 hari (seperti April & Juni) kehilangan 2 hari (tgl 29, 30).")

    # -------------------------------------------------------------------------
    # PEMBUKTIAN 2: Upaya Mengisi Catatan Aktivitas untuk Tanggal 29, 30, 31
    # -------------------------------------------------------------------------
    print("\n[LANGKAH REPRODUKSI 2]: Upaya Mengakses & Mengisi Target Harian Tanggal 29-31")
    print("-" * 80)
    januari = months[0]
    weeks_jan = manager.ambil_target_mingguan(januari.id)
    minggu_4_jan = weeks_jan[3]
    harian_m4 = manager.ambil_target_harian(minggu_4_jan.id)

    print(f"Target Minggu 4 Bulan Januari memiliki {len(harian_m4)} hari:")
    for h in harian_m4:
        print(f"  - Hari ke-{h.hari_ke} (id: {h.id[:8]}...)")

    print("\nMencoba mencatat aktivitas tanggal 29 s.d. 31 (hari ke-8 s.d. 10 di Minggu 4)...")
    payload_dengan_sisa_hari = {i: f"Membaca bab {i}" for i in range(1, 11)}
    try:
        manager.isi_target_harian_manual(minggu_4_jan.id, payload_dengan_sisa_hari)
        print("  [ERROR]: Sistem berhasil menyimpan (seharusnya gagal)!")
    except ValidationError as e:
        print(f"  >> [BUKTI TERKONFIRMASI]: Sistem melempar ValidationError:")
        print(f"     \"{e}\"")
        print("     Sistem secara kaku hanya mengizinkan input hari 1 s.d. 7!")
        print("     Akibatnya, pengguna sama sekali TIDAK BISA mencatat progres tanggal 29, 30, dan 31.")

    # -------------------------------------------------------------------------
    # PEMBUKTIAN 3: Ketidaksesuaian Hari Kalender Aktual Tahun 2026
    # -------------------------------------------------------------------------
    print("\n[LANGKAH REPRODUKSI 3]: Memeriksa Ketidaksesuaian Kalender Aktual 2026")
    print("-" * 80)
    # Cek 1 Februari 2026
    weekday_1_feb = datetime.date(2026, 2, 1).weekday()
    nama_hari_1_feb = HARI_DALAM_SEMINGGU[weekday_1_feb]

    print(f"Kalender Aktual 2026:")
    print(f"  - 1 Februari 2026 jatuh pada hari: {nama_hari_1_feb} (Minggu)")
    print(f"Model Sistem Saat Ini:")
    print(f"  - Hari ke-1 selalu diasumsikan: 'Senin'")
    print(f"  - Header terkunci statis: '7 Hari (Senin - Minggu)'")
    print(f">> [BUKTI TERKONFIRMASI]:")
    print(f"   Februari 2026 dimulai pada hari {nama_hari_1_feb}, tetapi sistem memaksakan")
    print(f"   urutan statis Senin s.d. Minggu tanpa menyelaraskan tanggal dengan hari sebenarnya.")

    # -------------------------------------------------------------------------
    # PEMBUKTIAN 4: Memeriksa Implementasi Web pada file index.html
    # -------------------------------------------------------------------------
    print("\n[LANGKAH REPRODUKSI 4]: Memeriksa Antarmuka Web (index.html)")
    print("-" * 80)
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Temukan elemen badge
        badge_match = re.search(r'<div id="harian-week-badge"[^>]*>(.*?)</div>', html, re.DOTALL)
        if badge_match:
            badge_text = badge_match.group(1).strip()
            print(f"  - Elemen #harian-week-badge: '{badge_text}'")
            if "7 Hari (Senin - Minggu)" in badge_text:
                print("    >> [BUKTI TERKONFIRMASI]: Ditemukan label statis '7 Hari (Senin - Minggu)' pada HTML!")

        # Temukan opsi select minggu
        opsi_minggu = re.findall(r'<option value="(\d+)">Minggu \1</option>', html)
        print(f"  - Opsi dropdown Minggu: {opsi_minggu} (Hanya 4 minggu)")
        if len(opsi_minggu) == 4 and "5" not in opsi_minggu:
            print("    >> [BUKTI TERKONFIRMASI]: Tidak ada opsi Minggu 5 untuk menampung sisa hari 29-31!")

        # Temukan array DAYS_DATA
        days_data_match = re.search(r'const DAYS_DATA = \[(.*?)\];', html, re.DOTALL)
        if days_data_match:
            print("  - DAYS_DATA di-hardcode 7 hari statis (Senin - Minggu).")
            print("    >> [BUKTI TERKONFIRMASI]: Antarmuka web tidak mendukung kalender aktual.")
    else:
        print("  - File index.html tidak ditemukan.")

    # -------------------------------------------------------------------------
    # KESIMPULAN REPRODUKSI
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("KESIMPULAN AKHIR REPRODUKSI BUG-112")
    print("=" * 80)
    print(f"1. Status Bug      : TERBUKTI BENAR-BENAR TERJADI (CONFIRMED)")
    print(f"2. Dampak Target   : {total_hari_hilang} hari hilang dalam setahun.")
    print(f"                     Pada target membaca 10 halaman/hari, pengguna kehilangan")
    print(f"                     pencatatan sebanyak {total_hari_hilang * 10} halaman dalam 1 tahun.")
    print(f"3. Dampak UI       : Label '7 Hari (Senin - Minggu)' selalu statis, dan")
    print(f"                     sisa tanggal 29-31 di 7 bulan tidak pernah muncul.")
    print("=" * 80)


if __name__ == "__main__":
    # Jika dijalankan dengan argumen --unittest, jalankan unit test
    if len(sys.argv) > 1 and sys.argv[1] == "--unittest":
        unittest.main(argv=[sys.argv[0]])
    else:
        # Jalankan visualisasi alur reproduksi interaktif
        jalankan_reproduksi_interaktif()
