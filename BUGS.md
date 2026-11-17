## BUG-112
- **Judul:** Ketidakkonsistenan dan Hilangnya Validasi Jumlah Hari pada Rincian Target Harian di Berbagai Pilihan Bulan
- **Langkah:** 
  1. Buka aplikasi web `https://monitoringtarget.vercel.app/`.
  2. Pada dropdown **-- Pilih Jenis Target --**, pilih opsi **Harian**.
  3. Pada filter **Bulan**, pilih bulan **Februari**, lalu pilih **Minggu 4** pada filter **Minggu**.
  4. Amati jumlah kartu harian yang dirender serta label durasi periode pada header bagian tersebut.
  5. Ulangi langkah 3 dengan memilih bulan dengan 31 hari (misalnya **Januari** atau **Maret**) pada **Minggu 4**.
- **Yang terjadi:** Bagian *Rincian Target Aktivitas Harian* menampilkan label statis **"7 Hari (Senin - Minggu)"** secara terus-menerus pada setiap minggu (Minggu 1 hingga Minggu 4) untuk semua bulan (total selalu dianggap 28 hari per bulan). Aplikasi tidak mengakomodasi sisa hari pada bulan dengan 30 atau 31 hari (tanggal 29–31 tidak pernah muncul/tidak bisa dilacak), serta tidak menyesuaikan pembagian hari kalender aktual (seperti Februari 2026 yang memiliki 28 hari dan dimulai pada hari Minggu, bukan Senin).
- **Yang seharusnya:** Sistem harus memetakan jumlah hari dan nama hari sesuai kalender aktual tahun 2026 (atau menyediakan tampilan/minggu tambahan untuk tanggal 29–31 pada bulan yang memiliki 30/31 hari), serta menampilkan rentang hari yang sesuai dengan minggu berjalan alih-alih mengunci label statis *"7 Hari (Senin - Minggu)"* di setiap minggu.
- **Dampak:** Pengguna tidak dapat mencatat atau memantau progres target membaca harian mereka pada tanggal 29, 30, dan 31 di 7 bulan dalam setahun (mengakibatkan hilangnya pelacakan sekitar 70 halaman target bacaan per bulan), serta menimbulkan kebingungan karena ketidaksesuaian antara hari kalender asli dengan jadwal hari di aplikasi.