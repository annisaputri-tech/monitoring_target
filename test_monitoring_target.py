import unittest
from monitoring_target import (
    TargetManager,
    YearlyTarget,
    MonthlyTarget,
    WeeklyTarget,
    DailyTarget,
    ValidationError
)


class TestMonitoringTarget(unittest.TestCase):
    def setUp(self):
        """Inisialisasi TargetManager sebelum setiap pengujian."""
        self.manager = TargetManager()

    # =========================================================================
    # KASUS 1: Pengguna dapat menambahkan minimal 1 target tahunan
    # =========================================================================
    def test_pengguna_dapat_menambahkan_minimal_satu_target_tahunan(self):
        """Memastikan pengguna dapat menambahkan minimal 1 target tahunan dengan

        indikator angka keberhasilan berupa nilai numerik (Sesuai US-01).
        """
        yearly_target = self.manager.tambah_target_tahunan(
            judul="Membaca 24 Buku",
            indikator_angka=24,
            satuan="buku"
        )

        self.assertIsNotNone(yearly_target)
        self.assertEqual(yearly_target.judul, "Membaca 24 Buku")
        self.assertEqual(yearly_target.indikator_angka, 24)
        self.assertIsInstance(yearly_target.indikator_angka, (int, float))

        # Memverifikasi minimal ada 1 target tahunan tersimpan
        semua_target = self.manager.ambil_semua_target_tahunan()
        self.assertGreaterEqual(len(semua_target), 1)

    def test_validasi_indikator_angka_harus_numerik(self):
        """Memastikan sistem menolak target tahunan jika indikator angka bukan numerik

        atau bernilai <= 0 (Kriteria Uji US-01 butir 3 & 4).
        """
        with self.assertRaises(ValidationError):
            self.manager.tambah_target_tahunan(
                judul="Target Tanpa Angka",
                indikator_angka="bukan_angka"  # Invalid
            )

        with self.assertRaises(ValidationError):
            self.manager.tambah_target_tahunan(
                judul="Target Angka Negatif",
                indikator_angka=-5  # Invalid
            )

    def test_pengguna_dapat_menambahkan_banyak_target_tahunan_tanpa_batas(self):
        """Memastikan pengguna dapat menambahkan lebih dari 1 target tanpa batasan

        maksimal (Kriteria Uji US-01 butir 2).
        """
        self.manager.tambah_target_tahunan("Membaca Buku", 24, "buku")
        self.manager.tambah_target_tahunan("Menabung", 36000000, "rupiah")
        self.manager.tambah_target_tahunan("Olahraga Lari", 500, "km")

        semua_target = self.manager.ambil_semua_target_tahunan()
        self.assertEqual(len(semua_target), 3)

    # =========================================================================
    # KASUS 2: Target tahunan terhubung dengan target bulanan (selama 12 bulan)
    # =========================================================================
    def test_target_tahunan_terhubung_dengan_12_target_bulanan(self):
        """Memastikan 1 target tahunan terhubung dengan tepat 12 target bulanan

        (Bulan 1 s.d. Bulan 12) sesuai US-02 dan alur.mmd.
        """
        yearly_target = self.manager.tambah_target_tahunan("Membaca 24 Buku", 24, "buku")

        # Sistem memecah target tahunan menjadi 12 slot target bulanan
        target_bulanan = self.manager.ambil_target_bulanan(yearly_target.id)

        # Harus ada tepat 12 bulan
        self.assertEqual(len(target_bulanan), 12)

        # Memastikan urutan bulan 1 s.d. 12 dan terhubung ke id target tahunan induknya
        for bulan_ke in range(1, 13):
            item = target_bulanan[bulan_ke - 1]
            self.assertEqual(item.bulan_ke, bulan_ke)
            self.assertEqual(item.yearly_target_id, yearly_target.id)

    # =========================================================================
    # KASUS 3: Target bulanan terhubung dengan target mingguan (4 minggu tiap bulan)
    # =========================================================================
    def test_target_bulanan_terhubung_dengan_4_target_mingguan(self):
        """Memastikan setiap target bulanan terhubung dengan tepat 4 target mingguan

        (Minggu 1 s.d. Minggu 4) sesuai alur.mmd dan hierarki PRD.
        """
        yearly_target = self.manager.tambah_target_tahunan("Membaca 24 Buku", 24, "buku")
        target_bulanan_list = self.manager.ambil_target_bulanan(yearly_target.id)
        target_bulan_1 = target_bulanan_list[0]

        # Sistem memecah target bulanan menjadi 4 target mingguan
        target_mingguan = self.manager.ambil_target_mingguan(target_bulan_1.id)

        self.assertEqual(len(target_mingguan), 4)

        for minggu_ke in range(1, 5):
            item = target_mingguan[minggu_ke - 1]
            self.assertEqual(item.minggu_ke, minggu_ke)
            self.assertEqual(item.monthly_target_id, target_bulan_1.id)

    # =========================================================================
    # KASUS 4: Target mingguan terhubung dengan target harian (1 minggu ada 7 hari)
    # =========================================================================
    def test_target_mingguan_terhubung_dengan_7_target_harian(self):
        """Memastikan setiap target mingguan terhubung dengan 7 aktivitas/tugas harian

        (Hari 1 s.d. Hari 7) sesuai alur.mmd dan hierarki PRD.
        """
        yearly_target = self.manager.tambah_target_tahunan("Membaca 24 Buku", 24, "buku")
        target_bulan_1 = self.manager.ambil_target_bulanan(yearly_target.id)[0]
        target_minggu_1 = self.manager.ambil_target_mingguan(target_bulan_1.id)[0]

        # Target mingguan terhubung dengan aktivitas untuk 7 hari
        target_harian = self.manager.ambil_target_harian(target_minggu_1.id)

        self.assertEqual(len(target_harian), 7)

        for hari_ke in range(1, 8):
            item = target_harian[hari_ke - 1]
            self.assertEqual(item.hari_ke, hari_ke)
            self.assertEqual(item.weekly_target_id, target_minggu_1.id)

    # =========================================================================
    # KASUS 5: Semua target ditulis secara manual oleh pengguna itu sendiri
    # =========================================================================
    def test_pengguna_mengisi_semua_tingkatan_target_secara_manual(self):
        """Memastikan semua target pada setiap tingkatan (tahunan, 12 bulanan,

        4 mingguan, 7 harian) diisi nilainya secara manual oleh pengguna,
        dan sistem memvalidasi kelengkapan isian manual tersebut.
        """
        # 1. Pengguna menulis target tahunan secara manual
        yearly_target = self.manager.tambah_target_tahunan(
            judul="Membaca 24 Buku",
            indikator_angka=24,
            satuan="buku"
        )
        self.assertEqual(yearly_target.judul, "Membaca 24 Buku")
        self.assertEqual(yearly_target.indikator_angka, 24)

        # 2. Pengguna mengisi nilai untuk 12 target bulanan secara manual
        input_manual_bulanan = {bulan: 2 for bulan in range(1, 13)}  # Contoh: 2 buku/bulan
        self.manager.isi_target_bulanan_manual(
            yearly_target_id=yearly_target.id,
            nilai_bulanan=input_manual_bulanan
        )
        daftar_bulan = self.manager.ambil_target_bulanan(yearly_target.id)
        for bulan in daftar_bulan:
            self.assertIsNotNone(bulan.nilai_target)
            self.assertEqual(bulan.nilai_target, 2)

        # 3. Pengguna mengisi target mingguan secara manual (4 minggu)
        bulan_pertama = daftar_bulan[0]
        input_manual_mingguan = {1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5}
        self.manager.isi_target_mingguan_manual(
            monthly_target_id=bulan_pertama.id,
            nilai_mingguan=input_manual_mingguan
        )
        daftar_minggu = self.manager.ambil_target_mingguan(bulan_pertama.id)
        for minggu in daftar_minggu:
            self.assertIsNotNone(minggu.nilai_target)
            self.assertEqual(minggu.nilai_target, 0.5)

        # 4. Pengguna menulis aktivitas harian secara manual (7 hari)
        minggu_pertama = daftar_minggu[0]
        input_manual_harian = {
            1: "Membaca Bab 1 (15 halaman)",
            2: "Membaca Bab 2 (15 halaman)",
            3: "Membaca Bab 3 (10 halaman)",
            4: "Membaca Bab 4 (15 halaman)",
            5: "Membaca Bab 5 (20 halaman)",
            6: "Membaca Bab 6 (15 halaman)",
            7: "Review dan rangkum buku"
        }
        self.manager.isi_target_harian_manual(
            weekly_target_id=minggu_pertama.id,
            aktivitas_harian=input_manual_harian
        )
        daftar_harian = self.manager.ambil_target_harian(minggu_pertama.id)
        for harian in daftar_harian:
            self.assertIsNotNone(harian.aktivitas)
            self.assertIn(harian.hari_ke, input_manual_harian)
            self.assertEqual(harian.aktivitas, input_manual_harian[harian.hari_ke])

    def test_validasi_penolakan_jika_target_bulanan_belum_terisi_lengkap(self):
        """Memastikan sistem menolak penyimpanan jika ada salah satu dari 12 bulan

        yang belum diisi secara manual oleh pengguna (US-02 Kriteria Uji #4 & alur.mmd).
        """
        yearly_target = self.manager.tambah_target_tahunan("Membaca 24 Buku", 24, "buku")

        # Pengguna hanya mengisi 11 bulan (Bulan 12 terlewat)
        input_tidak_lengkap = {bulan: 2 for bulan in range(1, 12)}

        with self.assertRaises(ValidationError):
            self.manager.isi_target_bulanan_manual(
                yearly_target_id=yearly_target.id,
                nilai_bulanan=input_tidak_lengkap
            )


if __name__ == "__main__":
    unittest.main()
