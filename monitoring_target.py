"""monitoring_target.py.

Modul inti untuk sistem monitoring target personal hierarkis
(Tahunan -> Bulanan -> Mingguan -> Harian).
"""

import calendar
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import uuid


class ValidationError(Exception):
    """Exception yang dilemparkan ketika validasi data target gagal."""
    pass


def hitung_total(
    bulan: Optional[int] = None,
    bulan_ke: Optional[int] = None,
    tahun: int = 2026
) -> int:
    """Menghitung total hari aktual pada tahun 2026 (atau tahun yang ditentukan).

    Sesuai perbaikan BUG-112:
    - 28 hari untuk Februari (bulan 2) pada tahun 2026
    - 30 hari untuk April (4), Juni (6), September (9), November (11)
    - 31 hari untuk Januari (1), Maret (3), Mei (5), Juli (7), Agustus (8), Oktober (10), Desember (12)
    - 365 hari untuk total satu tahun penuh (2026)

    Args:
        bulan: Nomor bulan (1 s.d. 12).
        bulan_ke: Nomor bulan (1 s.d. 12) sebagai alternatif parameter.
        tahun: Tahun kalender (default: 2026).

    Returns:
        Jumlah hari aktual (int) pada bulan tersebut, atau total hari setahun jika bulan tidak diisi.
    """
    b = bulan if bulan is not None else bulan_ke
    if b is not None:
        if not isinstance(b, int) or b < 1 or b > 12:
            raise ValidationError(f"Bulan {b} tidak valid. Harus bernilai 1 s.d. 12.")
        return calendar.monthrange(tahun, b)[1]

    return 366 if calendar.isleap(tahun) else 365


@dataclass
class DailyTarget:
    """Model data untuk target/aktivitas harian."""
    weekly_target_id: str
    hari_ke: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aktivitas: Optional[str] = None


@dataclass
class WeeklyTarget:
    """Model data untuk target mingguan."""
    monthly_target_id: str
    minggu_ke: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nilai_target: Optional[Union[int, float]] = None


@dataclass
class MonthlyTarget:
    """Model data untuk target bulanan."""
    yearly_target_id: str
    bulan_ke: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nilai_target: Optional[Union[int, float]] = None


@dataclass
class YearlyTarget:
    """Model data untuk target tahunan."""
    judul: str
    indikator_angka: Union[int, float]
    satuan: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


class TargetManager:
    """Manajer pengelola siklus hidup target tahunan, bulanan, mingguan, dan harian."""

    def __init__(self):
        self._yearly_targets: Dict[str, YearlyTarget] = {}
        self._monthly_targets: Dict[str, List[MonthlyTarget]] = {}
        self._weekly_targets: Dict[str, List[WeeklyTarget]] = {}
        self._daily_targets: Dict[str, List[DailyTarget]] = {}

    def hitung_total(
        self,
        target_id_atau_bulan: Optional[Union[str, int]] = None,
        bulan: Optional[int] = None,
        bulan_ke: Optional[int] = None,
        tahun: int = 2026
    ) -> int:
        """Menghitung total hari aktual untuk bulan tertentu, target tertentu, atau setahun penuh."""
        if isinstance(target_id_atau_bulan, int):
            return hitung_total(bulan=target_id_atau_bulan, tahun=tahun)
        elif isinstance(target_id_atau_bulan, str):
            if target_id_atau_bulan in self._yearly_targets:
                return sum(
                    len(self.ambil_target_harian(w.id))
                    for m in self.ambil_target_bulanan(target_id_atau_bulan)
                    for w in self.ambil_target_mingguan(m.id)
                )
            for y_id, m_list in self._monthly_targets.items():
                for m in m_list:
                    if m.id == target_id_atau_bulan:
                        return sum(len(self.ambil_target_harian(w.id)) for w in self.ambil_target_mingguan(m.id))
            if target_id_atau_bulan in self._daily_targets:
                return len(self._daily_targets[target_id_atau_bulan])
        b = bulan if bulan is not None else bulan_ke
        return hitung_total(bulan=b, tahun=tahun)

    def tambah_target_tahunan(
        self,
        judul: str,
        indikator_angka: Union[int, float],
        satuan: str = ""
    ) -> YearlyTarget:
        """Menambahkan target tahunan baru dan membentuk hierarki

        sesuai kalender aktual tahun 2026 (mengakomodasi seluruh hari aktual per bulan).
        """
        if not judul or not isinstance(judul, str) or not judul.strip():
            raise ValidationError("Judul target tahunan tidak boleh kosong.")

        if isinstance(indikator_angka, bool) or not isinstance(indikator_angka, (int, float)):
            raise ValidationError("Indikator angka harus berupa nilai numerik.")

        if indikator_angka <= 0:
            raise ValidationError("Indikator angka harus berupa nilai numerik lebih besar dari 0.")

        yearly_target = YearlyTarget(
            judul=judul.strip(),
            indikator_angka=indikator_angka,
            satuan=satuan.strip() if satuan else ""
        )
        self._yearly_targets[yearly_target.id] = yearly_target

        # 1. Bentuk hierarki 12 target bulanan
        monthly_list: List[MonthlyTarget] = []
        for bulan_ke in range(1, 13):
            m_target = MonthlyTarget(
                yearly_target_id=yearly_target.id,
                bulan_ke=bulan_ke
            )
            monthly_list.append(m_target)

            # 2. Hitung jumlah hari aktual di bulan tersebut pada tahun 2026 menggunakan hitung_total
            total_hari_bulan = hitung_total(bulan=bulan_ke, tahun=2026)

            # 3. Bentuk hierarki target mingguan dan harian berdasarkan pembagian hari aktual
            weekly_list: List[WeeklyTarget] = []
            hari_tersisa = total_hari_bulan
            minggu_ke = 1
            while hari_tersisa > 0:
                jumlah_hari_minggu_ini = min(7, hari_tersisa)
                w_target = WeeklyTarget(
                    monthly_target_id=m_target.id,
                    minggu_ke=minggu_ke
                )
                weekly_list.append(w_target)

                # Bentuk hierarki target harian untuk minggu ini
                daily_list: List[DailyTarget] = []
                for hari_ke in range(1, jumlah_hari_minggu_ini + 1):
                    d_target = DailyTarget(
                        weekly_target_id=w_target.id,
                        hari_ke=hari_ke
                    )
                    daily_list.append(d_target)
                self._daily_targets[w_target.id] = daily_list

                hari_tersisa -= jumlah_hari_minggu_ini
                minggu_ke += 1

            self._weekly_targets[m_target.id] = weekly_list

        self._monthly_targets[yearly_target.id] = monthly_list

        return yearly_target

    def ambil_semua_target_tahunan(self) -> List[YearlyTarget]:
        """Mengambil seluruh daftar target tahunan yang tersimpan."""
        return list(self._yearly_targets.values())

    def ambil_target_bulanan(self, yearly_target_id: str) -> List[MonthlyTarget]:
        """Mengambil daftar 12 target bulanan berdasarkan ID target tahunan."""
        if yearly_target_id not in self._yearly_targets:
            raise ValidationError(f"Target tahunan dengan id '{yearly_target_id}' tidak ditemukan.")
        return self._monthly_targets.get(yearly_target_id, [])

    def ambil_target_mingguan(self, monthly_target_id: str) -> List[WeeklyTarget]:
        """Mengambil daftar target mingguan berdasarkan ID target bulanan."""
        if monthly_target_id not in self._weekly_targets:
            raise ValidationError(f"Target bulanan dengan id '{monthly_target_id}' tidak ditemukan.")
        return self._weekly_targets.get(monthly_target_id, [])

    def ambil_target_harian(self, weekly_target_id: str) -> List[DailyTarget]:
        """Mengambil daftar target/aktivitas harian berdasarkan ID target mingguan."""
        if weekly_target_id not in self._daily_targets:
            raise ValidationError(f"Target mingguan dengan id '{weekly_target_id}' tidak ditemukan.")
        return self._daily_targets.get(weekly_target_id, [])

    def isi_target_bulanan_manual(
        self,
        yearly_target_id: str,
        nilai_bulanan: Dict[int, Union[int, float]]
    ) -> None:
        """Mengisi nilai target 12 bulan secara manual oleh pengguna.

        Menolak penyimpanan jika belum terisi lengkap untuk seluruh 12 bulan.
        """
        if yearly_target_id not in self._yearly_targets:
            raise ValidationError(f"Target tahunan dengan id '{yearly_target_id}' tidak ditemukan.")

        if not isinstance(nilai_bulanan, dict):
            raise ValidationError("Data nilai bulanan harus berupa dictionary {bulan: nilai}.")

        # Validasi kelengkapan 12 bulan (1..12)
        bulan_dibutuhkan = set(range(1, 13))
        if set(nilai_bulanan.keys()) != bulan_dibutuhkan:
            raise ValidationError("Target bulanan harus terisi lengkap untuk seluruh 12 bulan.")

        for bulan, nilai in nilai_bulanan.items():
            if isinstance(nilai, bool) or not isinstance(nilai, (int, float)):
                raise ValidationError(f"Nilai target untuk bulan {bulan} harus berupa nilai numerik.")
            if nilai < 0:
                raise ValidationError(f"Nilai target untuk bulan {bulan} tidak boleh bernilai negatif.")

        for m_target in self._monthly_targets[yearly_target_id]:
            m_target.nilai_target = nilai_bulanan[m_target.bulan_ke]

    def isi_target_mingguan_manual(
        self,
        monthly_target_id: str,
        nilai_mingguan: Dict[int, Union[int, float]]
    ) -> None:
        """Mengisi nilai target mingguan secara manual oleh pengguna."""
        if monthly_target_id not in self._weekly_targets:
            raise ValidationError(f"Target bulanan dengan id '{monthly_target_id}' tidak ditemukan.")

        if not isinstance(nilai_mingguan, dict):
            raise ValidationError("Data nilai mingguan harus berupa dictionary {minggu: nilai}.")

        minggu_tersedia = [w.minggu_ke for w in self._weekly_targets[monthly_target_id]]
        minggu_dibutuhkan = set(minggu_tersedia)
        if set(nilai_mingguan.keys()) != minggu_dibutuhkan and set(nilai_mingguan.keys()) != set(range(1, 5)):
            raise ValidationError(f"Target mingguan harus terisi lengkap untuk seluruh {len(minggu_dibutuhkan)} minggu.")

        for minggu, nilai in nilai_mingguan.items():
            if isinstance(nilai, bool) or not isinstance(nilai, (int, float)):
                raise ValidationError(f"Nilai target untuk minggu {minggu} harus berupa nilai numerik.")
            if nilai < 0:
                raise ValidationError(f"Nilai target untuk minggu {minggu} tidak boleh bernilai negatif.")

        for w_target in self._weekly_targets[monthly_target_id]:
            if w_target.minggu_ke in nilai_mingguan:
                w_target.nilai_target = nilai_mingguan[w_target.minggu_ke]

    def isi_target_harian_manual(
        self,
        weekly_target_id: str,
        aktivitas_harian: Dict[int, str]
    ) -> None:
        """Mengisi catatan aktivitas harian untuk seluruh hari pada minggu terkait secara manual."""
        if weekly_target_id not in self._daily_targets:
            raise ValidationError(f"Target mingguan dengan id '{weekly_target_id}' tidak ditemukan.")

        if not isinstance(aktivitas_harian, dict):
            raise ValidationError("Data aktivitas harian harus berupa dictionary {hari: aktivitas}.")

        hari_tersedia = [d.hari_ke for d in self._daily_targets[weekly_target_id]]
        hari_dibutuhkan = set(hari_tersedia)
        if set(aktivitas_harian.keys()) != hari_dibutuhkan:
            raise ValidationError(f"Aktivitas harian harus terisi lengkap untuk seluruh {len(hari_dibutuhkan)} hari.")

        for hari, aktivitas in aktivitas_harian.items():
            if not aktivitas or not isinstance(aktivitas, str) or not aktivitas.strip():
                raise ValidationError(f"Aktivitas harian untuk hari {hari} tidak boleh kosong.")

        for d_target in self._daily_targets[weekly_target_id]:
            d_target.aktivitas = aktivitas_harian[d_target.hari_ke].strip()
