Product Requirements Document (PRD): Sistem Monitoring Target Tahunan Personal
Status: Draf v1.0
Pemilik Produk: Product Manager (Pengguna Tunggal)
Target Rilis: Q4 2026 (Siap digunakan penuh untuk siklus target tahun 2027)
1. Latar Belakang & Pernyataan Masalah
Pernyataan Masalah: Pengguna mengalami kesulitan dalam melacak dan menghubungkan eksekusi kegiatan harian, mingguan, dan bulanan terhadap target jangka panjang. Ketiadaan sistem pemantauan yang terstruktur menyebabkan hilangnya visibilitas progres, turunnya konsistensi di pertengahan tahun, dan gagalnya pencapaian target tahunan.
Target Pengguna: Pengguna tunggal (diri sendiri) yang membutuhkan sistem personal yang ringan, bebas hambatan (low-friction), dan terfokus pada eksekusi rutin.
2. Tujuan Terukur (Success Metrics)
Keberhasilan sistem ini diukur melalui empat metrik utama dalam 6 bulan pertama penggunaan:
Tingkat Penyelesaian Target Tahunan: Meningkat dari 0% (tidak tercapai) menjadi minimal 80% dari total target tahunan yang ditetapkan.
Konsistensi Pencatatan Harian (Check-in Rate): Pengguna melakukan pembaruan status kegiatan harian minimal 6 dari 7 hari setiap minggu (≥ 85% konsistensi).
Kepatuhan Review Berkala: Menyelesaikan 100% sesi evaluasi mingguan (4 kali/bulan) dan evaluasi bulanan (12 kali/tahun) tepat waktu.
Kecepatan Pencatatan (Time-to-Log): Waktu yang dibutuhkan untuk mencatat penyelesaian tugas harian atau melihat status progres tidak lebih dari 30 detik per sesi.
3. Fitur Utama & Prioritas
Fitur disusun berdasarkan kerangka prioritas MoSCoW (Must-have, Should-have, Could-have) untuk memastikan fokus pada penyelesaian masalah inti terlebih dahulu:
Prioritas
Nama Fitur
Deskripsi & Nilai Utama
P0 (Must-have)
1. Hierarki Target (Goal Cascading)
Memecah target tahunan menjadi tonggak pencapaian (milestone) bulanan, target mingguan, dan daftar tugas harian yang saling terhubung secara otomatis.
P0 (Must-have)
2. Dasbor Harian & Pelacak Kebiasaan (Daily Tracker)
Tampilan antarmuka satu layar berisi daftar tugas hari ini (to-do) dan habit tracker dengan aksi centang (check-off) satu klik untuk mengurangi friksi pencatatan.
P1 (Should-have)
3. Kalkulator Progres Otomatis
Menghitung persentase pencapaian bulanan dan tahunan secara real-time berdasarkan akumulasi tugas harian dan mingguan yang selesai.
P1 (Should-have)
4. Ritual Evaluasi Mingguan & Bulanan (Review Wizard)
Formulir terpandu yang muncul setiap akhir minggu/bulan untuk meninjau tugas yang tertunda, mencatat hambatan, dan menjadwalkan ulang (reschedule) target bulan berikutnya.
P2 (Could-have)
5. Pengingat Cerdas & Streak Alert
Notifikasi terjadwal pada pagi hari (daftar fokus hari ini) dan malam hari (pengingat check-in), dilengkapi indikator rantai konsistensi (streak) untuk menjaga motivasi.

4. Alur Pengguna Langkah demi Langkah (User Flow)
Alur A: Perencanaan Awal Tahun (Setup)
Pengguna membuka aplikasi dan masuk ke menu Target Tahunan.
Pengguna membuat minimal 1 target tahunan beserta indikator angka keberhasilannya (contoh: "Membaca 24 buku" atau "Menabung Rp36 juta"). Untuk jumlahnya boleh lebih dari 1 target.
Sistem memandu pengguna memecah setiap target tahunan menjadi 12 target bulanan (contoh: "2 buku/bulan").
Pengguna menurunkan target bulan berjalan menjadi target mingguan dan tugas/kebiasaan harian.
Pengguna tidak dapat checklist tugas kemarin jika terlambat. Walaupun hari ini dikerjakan. (Harus disiplin waktu).Jika ingin checklist selesai tugas yang kemarin, harus tunggu evaluasi mingguan terlebih dahulu saat status tugas sudah dipindah ke minggu depan.
Alur B: Eksekusi & Pencatatan Harian (Daily Loop)
Pengguna membuka Dasbor Harian pada pagi hari untuk melihat daftar tugas yang jatuh tempo hari ini.
Sepanjang hari atau pada malam hari, pengguna menandai tugas yang selesai dengan satu klik (checklist).
Sistem secara otomatis memperbarui bar persentase pada target mingguan, bulanan, dan tahunan terkait.
Alur C: Evaluasi Berkala (Weekly & Monthly Review)
Setiap hari Minggu pukul 19.00, sistem menampilkan banner Waktunya Evaluasi Mingguan.
Pengguna meninjau ringkasan skor minggu tersebut (contoh: 85% tugas selesai).
Untuk tugas yang belum selesai, pengguna memilih opsi: Pindahkan ke minggu depan, Ubah target, atau Hapus.
Pengguna menyetujui rencana minggu berikutnya dan menutup sesi evaluasi.
5. Daftar di Luar Cakupan (Out of Scope)
Untuk mencegah pembengkakan fitur (scope creep) dan menjaga aplikasi tetap cepat dibangun:
Fitur Multi-Pengguna & Kolaborasi: Tidak ada sistem berbagi target, komentar tim, papan peringkat (leaderboard), atau manajemen hak akses peran (role-based access).
Integrasi Kalender Eksternal Pihak Ketiga: Belum mendukung sinkronisasi dua arah dengan Google Calendar, Apple Calendar, atau Outlook pada versi 1.0.
Analitik AI / Prediksi Otomatis: Tidak ada rekomendasi jadwal berbasis kecerdasan buatan; seluruh penyesuaian target dilakukan secara sadar oleh pengguna saat sesi evaluasi.
Aplikasi Mobile Native (iOS/Android): Pengembangan difokuskan pada aplikasi berbasis web responsif (Progressive Web App) agar dapat diakses dari desktop maupun peramban ponsel tanpa proses publikasi ke App Store/Play Store.
6. Kriteria Selesai yang Bisa Diuji (Acceptance Criteria)
Sistem dinyatakan selesai dan siap digunakan apabila lolos seluruh skenario pengujian berikut:
AC-01 (Keterhubungan Hierarki):
Given pengguna memiliki target tahunan "100 jam belajar" yang terhubung dengan target bulanan "10 jam belajar",
When pengguna menyelesaikan tugas harian berdurasi "2 jam belajar",
Then progres bulanan otomatis bertambah menjadi 20% dan progres tahunan bertambah menjadi 2% tanpa perlu input ulang.
AC-02 (Kecepatan Pencatatan):
Given pengguna berada di halaman utama (Dasbor Harian),
When pengguna mencentang 3 tugas harian yang telah selesai,
Then seluruh aksi tersimpan dan status visual berubah dalam waktu kurang dari 2 detik tanpa memuat ulang halaman (page reload).
AC-03 (Penanganan Tugas Tertunda saat Review):
Given terdapat 2 tugas mingguan yang belum dicentang hingga akhir hari Minggu,
When pengguna menjalankan alur Review Mingguan dan memilih "Pindahkan ke minggu depan",
Then kedua tugas tersebut otomatis muncul di daftar tugas minggu berikutnya dengan label status "Tertunda" dan tidak terhitung sebagai tugas selesai pada minggu sebelumnya.
AC-04 (Persistensi Data):
Given pengguna telah memperbarui progres harian dan menutup peramban (browser),
When pengguna membuka kembali sistem pada perangkat yang sama atau berbeda,
Then seluruh data riwayat harian, persentase bulanan, dan catatan evaluasi tetap tersimpan secara akurat tanpa ada data yang hilang.

