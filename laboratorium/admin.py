# laboratorium/admin.py

from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Laboratorium, KategoriUtama, KategoriAlat, UnitAlat, Peminjaman, Pengembalian, JadwalLab, PLP

# --- TAMBAHKAN KELAS BARU INI ---
class JadwalLabInline(admin.TabularInline):
    model = JadwalLab
    extra = 1

# Mengatur tampilan untuk Laboratorium (tidak ada perubahan)
@admin.register(Laboratorium)
class LaboratoriumAdmin(admin.ModelAdmin):
    list_display = ('kode_ruang', 'nama', 'gambar')
    inlines = [JadwalLabInline]

@admin.register(PLP)
class PLPAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'nip')

@admin.register(KategoriUtama)
class KategoriUtamaAdmin(admin.ModelAdmin):
    list_display = ('nama',)

# --- BAGIAN BARU: MENAMPILKAN KATEGORI ALAT ---
# Ini akan memunculkan menu "Kategori Alat" di admin
@admin.register(KategoriAlat)
class KategoriAlatAdmin(admin.ModelAdmin):
    # Tampilkan Kategori Utama dan Jumlah Unit
    list_display = ('nama', 'kategori_utama', 'jumlah_unit')
    # Tambahkan filter berdasarkan Kategori Utama
    list_filter = ('kategori_utama',)
    search_fields = ('nama',)

    # Fungsi custom untuk menghitung jumlah unit
    def jumlah_unit(self, obj):
        # Menghitung berapa banyak UnitAlat yang terhubung ke KategoriAlat ini
        return obj.unit_alat.count()

    jumlah_unit.short_description = "Jumlah Unit Terdaftar"

# --- BAGIAN BARU: MENAMPILKAN UNIT ALAT ---
# Ini akan memunculkan menu "Unit Alat", tempat Anda mengisi detail
@admin.register(UnitAlat)
class UnitAlatAdmin(admin.ModelAdmin):
    # Kolom-kolom ini akan tampil di daftar Unit Alat
    list_display = ('tipe_atau_merk', 'kategori', 'serial_number', 'status', 'kondisi', 'tahun_perolehan', 'tampilan_foto')
    # Filter di sisi kanan untuk mempermudah pencarian
    list_filter = ('kategori', 'status', 'kondisi', 'tahun_perolehan')
    # Kolom yang bisa dicari
    search_fields = ('tipe_atau_merk', 'serial_number')

    # Tambahkan fungsi untuk menampilkan thumbnail
    def tampilan_foto(self, obj):
        if obj.foto:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:8px;" />', obj.foto.url)
        return "No Image"
    tampilan_foto.short_description = 'Foto'

# --- BAGIAN YANG DIPERBARUI: MENAMPILKAN PEMINJAMAN ---
# LOKASI: laboratorium/admin.py
# ... (admin untuk Laboratorium, KategoriAlat, Alat biarkan sama) ...


# --- GANTI KESELURUHAN KELAS DI BAWAH INI ---

@admin.register(Peminjaman)
class PeminjamanAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'peminjam', 'unit_alat', 'laboratorium', 'status_peminjaman')
    
    # Filter disesuaikan dengan field yang ada dan relevan
    list_filter = ('status_peminjaman', 'laboratorium', 'unit_alat__kategori')
    
    # Search disesuaikan dengan field yang ada
    search_fields = ('nama_lengkap', 'nrp_nip', 'unit_alat__tipe_atau_merk')
    
    # Readonly fields disesuaikan, 'tanggal_pinjam' dibuat otomatis dan tidak perlu di sini
    # Kode baru yang benar
    readonly_fields = ('laboratorium', 'peminjam', 'unit_alat', 'is_alat_baru', 'nama_alat_baru', 'tipe_alat_baru', 'sn_alat_baru', 'nama_lengkap', 'status_peminjam', 'nrp_nip', 'nomor_telepon', 'dosen_perkuliahan', 'nama_plp', 'catatan_kondisi')
    # --- FUNGSI DENGAN INDENTASI YANG SUDAH DIPERBAIKI ---
    def save_model(self, request, obj, form, change):
        try:
            original_status = Peminjaman.objects.get(pk=obj.pk).status_peminjaman
        except Peminjaman.DoesNotExist:
            original_status = None
        
        super().save_model(request, obj, form, change)
        
        new_status = obj.status_peminjaman
        
        # Pengecekan utama: Apakah peminjaman ini terhubung ke UnitAlat?
        if obj.unit_alat:
            unit = obj.unit_alat
            if new_status == 'Disetujui' and original_status == 'Menunggu Persetujuan':
                if unit.status == 'Tersedia':
                    unit.status = 'Dipinjam'
                    unit.save()
                    self.message_user(request, f"Peminjaman untuk '{unit}' disetujui.", messages.SUCCESS)
                else:
                    obj.status_peminjaman = 'Ditolak'
                    obj.save()
                    self.message_user(request, f"GAGAL. Alat '{unit}' sudah berstatus '{unit.status}'.", messages.ERROR)
            
            if original_status == 'Disetujui' and (new_status == 'Dikembalikan' or new_status == 'Ditolak'):
                unit.status = 'Tersedia'
                unit.save()
                self.message_user(request, f"Status diubah. Stok untuk '{unit}' telah dikembalikan.", messages.INFO)
        else:
            # Jika TIDAK (artinya ini "alat baru"), tidak ada logika stok yang dijalankan.
            # Ini mencegah error. Kita bisa tambahkan pesan jika perlu.
            self.message_user(request, f"Perubahan status untuk peminjaman alat baru '{obj.nama_alat_baru}' telah disimpan.", messages.INFO)

# (Biarkan PengembalianAdmin jika Anda masih menggunakannya)
@admin.register(Pengembalian)
class PengembalianAdmin(admin.ModelAdmin):
    list_display = ('nama_pengembali', 'peminjaman', 'tanggal_pengembalian', 'kondisi_barang', 'status', 'lihat_bukti')
    list_filter = ('status', 'tanggal_pengembalian', 'kondisi_barang')
    search_fields = ('peminjaman__nama_lengkap', 'peminjaman__alat__nama')
    readonly_fields = ('peminjaman', 'tanggal_pengembalian', 'lihat_bukti')

    def lihat_bukti(self, obj):
        if obj.bukti_peminjaman:
            return format_html('<a href="{}" target="_blank">Lihat File PDF</a>', obj.bukti_peminjaman.url)
        return "Tidak ada file di-upload"
    lihat_bukti.short_description = "Bukti Peminjaman"

    def save_model(self, request, obj, form, change):
        try:
            original_status = Pengembalian.objects.get(pk=obj.pk).status
        except Pengembalian.DoesNotExist:
            original_status = None

        super().save_model(request, obj, form, change)
        new_status = obj.status
        
        # Hanya jalankan logika jika status diubah menjadi 'Diterima'
        if new_status == 'Diterima' and original_status != 'Diterima':
            peminjaman_record = obj.peminjaman
            
            # Cek apakah peminjaman ini untuk alat terdaftar atau alat baru
            if peminjaman_record.unit_alat:
                # --- JIKA INI ALAT STANDAR ---
                unit_alat_dikembalikan = peminjaman_record.unit_alat
                unit_alat_dikembalikan.status = 'Tersedia'
                unit_alat_dikembalikan.save()
                self.message_user(request, f"Pengembalian diterima. Stok untuk {unit_alat_dikembalikan} telah dikembalikan.", messages.SUCCESS)
            else:
                # --- JIKA INI ALAT BARU YANG DIINPUT MANUAL ---
                self.message_user(request, f"Pengembalian untuk alat baru '{peminjaman_record.nama_alat_baru}' telah diterima.", messages.SUCCESS)

            # Setelah itu, tandai peminjaman sebagai selesai
            peminjaman_record.status_peminjaman = 'Dikembalikan'
            peminjaman_record.save()

            #self.message_user(request, f"Pengembalian diterima. Stok untuk {unit_alat_dikembalikan} telah dikembalikan.", messages.SUCCESS)

