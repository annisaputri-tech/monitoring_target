"""test_regresi.py.

Uji Regresi untuk BUG-112:
Ketidakkonsistenan dan Hilangnya Validasi Jumlah Hari pada Rincian Target Harian di Berbagai Pilihan Bulan.

Laporan:
Pada halaman Monitoring Target (https://monitoringtarget.vercel.app/), ketika pengguna memilih
Jenis Target "Harian" dan memilih bulan yang memiliki 31 hari (seperti Januari), sistem harus
mengakomodasi seluruh 31 hari tersebut (misalnya dengan menyediakan opsi Minggu ke-5 atau
menyesuaikan jumlah hari pada minggu terakhir) serta menampilkan jumlah hari yang sesuai dengan
kalender aktual tahun 2026, bukan mengunci tampilan pada 4 minggu dengan label statis
"7 Hari (Senin - Minggu)" (total 28 hari) yang menyebabkan tanggal 29, 30, dan 31 hilang
dan tidak dapat dilacak.
"""

import os
import unittest
from monitoring_target import (
    TargetManager,
    YearlyTarget,
    MonthlyTarget,
    WeeklyTarget,
    DailyTarget,
    ValidationError
)


class TestRegresiMonitoringTarget(unittest.TestCase):
    """Test suite uji regresi untuk BUG-112 pada sistem monitoring target."""

    def setUp(self):
        """Inisialisasi TargetManager sebelum setiap pengujian."""
        self.manager = TargetManager()

    # BUG-112
    def test_target_harian_bulan_31_hari_mengakomodasi_seluruh_hari_dan_kalender_2026(self):
        """Memastikan sistem mengakomodasi seluruh 31 hari pada bulan Januari

        (misalnya dengan menyediakan opsi Minggu ke-5 atau menyesuaikan jumlah hari
        pada minggu terakhir) serta menampilkan jumlah hari yang sesuai dengan kalender
        aktual tahun 2026, bukan mengunci tampilan pada 4 minggu dengan label statis
        '7 Hari (Senin - Minggu)' (total 28 hari) yang menyebabkan tanggal 29, 30,
        dan 31 hilang dan tidak dapat dilacak.
        """
        # 1. Tambahkan target tahunan
        yearly_target = self.manager.tambah_target_tahunan(
            judul="Membaca 24 Buku Target 2026",
            indikator_angka=24,
            satuan="buku"
        )

        # 2. Ambil target bulan ke-1 (Januari: memiliki 31 hari pada kalender aktual 2026)
        daftar_bulan = self.manager.ambil_target_bulanan(yearly_target.id)
        januari = daftar_bulan[0]
        self.assertEqual(januari.bulan_ke, 1)

        # 3. Ambil seluruh target mingguan untuk bulan Januari
        daftar_minggu = self.manager.ambil_target_mingguan(januari.id)

        # 4. Kumpulkan seluruh target harian dari semua minggu di bulan Januari
        semua_target_harian = []
        for minggu in daftar_minggu:
            target_harian_minggu = self.manager.ambil_target_harian(minggu.id)
            semua_target_harian.extend(target_harian_minggu)

        total_hari_januari = len(semua_target_harian)

        # 5. Sistem harus mengakomodasi seluruh 31 hari, bukan hanya 28 hari
        self.assertEqual(
            total_hari_januari,
            31,
            f"Bulan Januari seharusnya mengakomodasi seluruh 31 hari target harian sesuai kalender aktual tahun 2026, "
            f"namun sistem hanya mengakomodasi {total_hari_januari} hari (tanggal 29, 30, dan 31 hilang dan tidak dapat dilacak)."
        )

        # 6. Sistem harus menyediakan opsi minggu tambahan (misal Minggu ke-5) atau pembagian minggu
        # yang memadai untuk menampung sisa hari (tanggal 29, 30, dan 31)
        self.assertGreaterEqual(
            len(daftar_minggu),
            5,
            "Sistem harus menyediakan opsi Minggu ke-5 atau pembagian minggu yang memadai "
            "untuk menampung tanggal 29, 30, dan 31."
        )

        # 7. Verifikasi antarmuka web (index.html):
        # Tampilan tidak boleh mengunci label statis '7 Hari (Senin - Minggu)'
        html_path = os.path.join(os.path.dirname(__file__), "index.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            self.assertNotIn(
                "7 Hari (Senin - Minggu)",
                html_content,
                "Tampilan antarmuka web tidak boleh mengunci label statis '7 Hari (Senin - Minggu)'."
            )


if __name__ == "__main__":
    unittest.main()
