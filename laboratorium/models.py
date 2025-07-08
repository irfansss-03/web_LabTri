# laboratorium/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

class PLP(models.Model):
    nama_lengkap = models.CharField(max_length=150)
    nip = models.CharField(max_length=50, unique=True, verbose_name="NIP")
    foto = models.ImageField(upload_to='foto_plp/')
    def __str__(self):
        return self.nama_lengkap

class Laboratorium(models.Model):
    kode_ruang = models.CharField(max_length=20, unique=True, verbose_name="Kode Ruang Lab")
    nama = models.CharField(max_length=100, unique=True)
    gambar = models.ImageField(upload_to='lab_images/', blank=True, null=True)
    deskripsi = models.TextField(max_length=2000, blank=True, null=True, help_text="Deskripsi tentang laboratorium")
    plp = models.ForeignKey(PLP, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="PLP Penanggung Jawab")
    def __str__(self):
        return self.nama

class KategoriUtama(models.Model):
    nama = models.CharField(max_length=100, unique=True, verbose_name="Nama Kategori Utama")
    class Meta:
        # Mengubah nama yang tampil di admin panel
        verbose_name_plural = "1. Kategori Alat"
    def __str__(self):
        return self.nama

class KategoriAlat(models.Model):
    kategori_utama = models.ForeignKey(KategoriUtama, on_delete=models.CASCADE, related_name="sub_kategori")
    nama = models.CharField(max_length=100, unique=True, help_text="Contoh: Raspberry Pi, Proyektor, Mouse")
    class Meta:
        # Mengubah nama yang tampil di admin panel
        verbose_name_plural = "2. Jenis Alat"
    def __str__(self):
        return f"{self.nama} (di bawah {self.kategori_utama.nama})"

class UnitAlat(models.Model):
    KONDISI_CHOICES = [('Baik', 'Baik'), ('Perlu Perbaikan', 'Perlu Perbaikan'), ('Rusak', 'Rusak')]
    STATUS_CHOICES = [('Tersedia', 'Tersedia'), ('Dipinjam', 'Dipinjam')]
    kategori = models.ForeignKey(KategoriAlat, on_delete=models.CASCADE, related_name="unit_alat")
    tipe_atau_merk = models.CharField(max_length=100, help_text="Contoh: Raspberry Pi 4 Model B")
    serial_number = models.CharField(max_length=100, unique=True)
    tahun_perolehan = models.PositiveIntegerField(help_text="Tahun alat ini dibeli/diterima")
    kondisi = models.CharField(max_length=100, choices=KONDISI_CHOICES, default='Baik')
    foto = models.ImageField(upload_to='foto_alat/', blank=True, null=True, verbose_name="Foto Alat")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Tersedia')
    class Meta:
        verbose_name_plural = "3. Unit Alat"
        ordering = ['kategori', 'tipe_atau_merk']
    def __str__(self):
        return f"{self.tipe_atau_merk} (SN: {self.serial_number})"

class JadwalLab(models.Model):
    laboratorium = models.ForeignKey(Laboratorium, on_delete=models.CASCADE, related_name="jadwal")
    gambar_jadwal = models.ImageField(upload_to='jadwal_lab/')
    keterangan = models.CharField(max_length=255, blank=True, null=True, help_text="Contoh: Jadwal Praktikum Ganjil 2025")
    class Meta:
        verbose_name_plural = "Jadwal Lab"
    def __str__(self):
        return f"Jadwal untuk {self.laboratorium.nama} - {self.keterangan}"

class Peminjaman(models.Model):
    STATUS_CHOICES = [('Menunggu Persetujuan', 'Menunggu Persetujuan'), ('Disetujui', 'Disetujui'), ('Ditolak', 'Ditolak'), ('Dikembalikan', 'Dikembalikan')]
    STATUS_PEMINJAM_CHOICES = [('Mahasiswa', 'Mahasiswa'), ('Dosen', 'Dosen'), ('Karyawan', 'Karyawan')]
    laboratorium = models.ForeignKey(Laboratorium, on_delete=models.SET_NULL, null=True)
    peminjam = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False)
    unit_alat = models.ForeignKey(UnitAlat, on_delete=models.PROTECT, null=True, blank=True)
    is_alat_baru = models.BooleanField(default=False, verbose_name="Apakah ini alat baru?")
    nama_alat_baru = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nama Alat Baru")
    tipe_alat_baru = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipe/Merk Alat Baru")
    sn_alat_baru = models.CharField(max_length=100, blank=True, null=True, verbose_name="Serial Number (Opsional)")
    nama_lengkap = models.CharField(max_length=150)
    status_peminjam = models.CharField(max_length=20, choices=STATUS_PEMINJAM_CHOICES)
    nrp_nip = models.CharField(max_length=30, verbose_name="NRP/NIP")
    nomor_telepon = models.CharField(max_length=20)
    dosen_perkuliahan = models.CharField(max_length=150)
    nama_plp = models.CharField(max_length=150)
    catatan_kondisi = models.TextField(help_text="Isi dengan kondisi barang saat Anda pinjam (contoh: ada goresan kecil di bodi)", verbose_name="Catatan Kondisi Barang Saat Dipinjam")
    status_peminjaman = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Menunggu Persetujuan')
    tanggal_kembali = models.DateField(blank=True, null=True)
    kondisi_saat_kembali = models.CharField(max_length=20, choices=UnitAlat.KONDISI_CHOICES, blank=True, null=True)
    tanggal_pinjam = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-pk']
        verbose_name_plural = "Data Peminjaman"
    def __str__(self):
        if self.is_alat_baru:
            return f"Alat Baru: {self.nama_alat_baru} oleh {self.nama_lengkap}"
        elif self.unit_alat:
            return f"{self.unit_alat} oleh {self.nama_lengkap}"
        return f"Peminjaman oleh {self.nama_lengkap}"

class Pengembalian(models.Model):
    STATUS_KEMBALI_CHOICES = [('Menunggu Konfirmasi', 'Menunggu Konfirmasi'), ('Diterima', 'Diterima')]
    KONDISI_CHOICES = [('Baik', 'Baik'), ('Rusak', 'Rusak'), ('Minus', 'Minus')]
   # Kode BARU yang Benar
    peminjaman = models.ForeignKey(Peminjaman, on_delete=models.CASCADE)
    nama_pengembali = models.CharField(max_length=150, verbose_name="Nama Lengkap Pengembali", default="")
    bukti_peminjaman = models.FileField(upload_to='bukti_kembali/', blank=True, null=True, verbose_name="Upload Bukti Peminjaman (Opsional)")
    tanggal_pengembalian = models.DateField(auto_now_add=True)
    kondisi_barang = models.CharField(max_length=20, choices=KONDISI_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_KEMBALI_CHOICES, default='Menunggu Konfirmasi')
    nama_plp = models.CharField(max_length=150, help_text="Isi dengan nama PLP yang menerima barang")
    class Meta:
        ordering = ['-tanggal_pengembalian']
        verbose_name_plural = "Data Pengembalian"
    def __str__(self):
        if self.peminjaman:
            return f"Pengembalian untuk {self.peminjaman}"
        return f"Pengembalian ID: {self.pk}"