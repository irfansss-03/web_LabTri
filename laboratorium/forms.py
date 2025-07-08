# laboratorium/forms.py

from django import forms
from .models import Peminjaman, Pengembalian, UnitAlat # Pastikan import sudah benar

class PeminjamanForm(forms.ModelForm):
    class Meta:
        model = Peminjaman
        fields = [
            'nama_lengkap', 'status_peminjam', 'nrp_nip', 'nomor_telepon', 
            'dosen_perkuliahan', 'nama_plp', 'catatan_kondisi'
        ]

    def clean_nrp_nip(self):
        data = self.cleaned_data.get('nrp_nip')
        if data and not data.isdigit():
            raise forms.ValidationError("NRP/NIP hanya boleh berisi angka.")
        return data

    def clean_nomor_telepon(self):
        data = self.cleaned_data.get('nomor_telepon')
        if data and not data.isdigit():
            raise forms.ValidationError("Nomor telepon hanya boleh berisi angka.")
        return data

class PengembalianForm(forms.ModelForm):
    class Meta:
        model = Pengembalian
        fields = ['peminjaman', 'nama_pengembali', 'kondisi_barang', 'nama_plp', 'bukti_peminjaman']
        labels = {
            'nama_plp': 'PIC/PLP Laboratorium',  # Ganti "Nama PLP" menjadi "Nama PLP Penerima"
        }

    def __init__(self, *args, **kwargs):
        lab_pk = kwargs.pop('lab_pk', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set queryset awal menjadi kosong
        self.fields['peminjaman'].queryset = Peminjaman.objects.none()

        if user:
            # --- PERUBAHAN UTAMA ADA DI SINI ---
            # 1. Ambil ID peminjaman yang pengembaliannya sudah DITERIMA oleh admin.
            peminjaman_selesai = Pengembalian.objects.filter(
                status='Diterima'
            ).values_list('peminjaman_id', flat=True)

            # 2. Ambil semua peminjaman aktif (Disetujui) milik user ini.
            peminjaman_aktif = Peminjaman.objects.filter(
                peminjam=user,
                status_peminjaman='Disetujui'
            )

            # 3. Filter lagi berdasarkan lab jika perlu.
            if lab_pk:
                peminjaman_aktif = peminjaman_aktif.filter(laboratorium_id=lab_pk)
            
            # 4. KECUALIKAN hanya peminjaman yang sudah benar-benar selesai.
            queryset_final = peminjaman_aktif.exclude(pk__in=peminjaman_selesai)
            
            self.fields['peminjaman'].queryset = queryset_final
            self.fields['peminjaman'].label = "Pilih Peminjaman yang Akan Dikembalikan"

    def clean(self):
        cleaned_data = super().clean()
        peminjaman_obj = cleaned_data.get('peminjaman')
        bukti_file = cleaned_data.get('bukti_peminjaman')

        if peminjaman_obj:
            if peminjaman_obj.is_alat_baru and not bukti_file:
                raise forms.ValidationError(
                    "Untuk pengembalian 'alat baru', Anda wajib mengunggah kembali file bukti peminjaman (PDF)."
                )
        return cleaned_data 