# laboratorium/views.py
import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Laboratorium, KategoriAlat, UnitAlat, Peminjaman, Pengembalian, KategoriUtama
from .forms import PeminjamanForm, PengembalianForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.views import LogoutView

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Cek apakah user bukan staff/superuser (asumsi user prodi bukan staff)
            if not user.is_staff:
                login(request, user)
                return redirect('dashboard')
            else:
                error = "Halaman ini hanya untuk login Prodi/Mahasiswa."
        else:
            error = "Username atau password salah."
    return render(request, 'laboratorium/login.html', {'error': error})

@login_required(login_url='/login/')
def dashboard_view(request):
    laboratories = Laboratorium.objects.all()
    return render(request, 'laboratorium/dashboard.html', {'laboratories': laboratories})

@login_required(login_url='/login/')
def lab_detail_view(request, lab_pk):
    lab = get_object_or_404(Laboratorium, pk=lab_pk)
    jadwal_list = lab.jadwal.all()
    context = {'lab': lab, 'jadwal_list': jadwal_list}
    return render(request, 'laboratorium/lab_detail.html', context)

@login_required(login_url='/login/')
def deskripsi_lab_view(request, lab_pk):
    lab = get_object_or_404(Laboratorium, pk=lab_pk)
    context = {'lab': lab}
    return render(request, 'laboratorium/deskripsi_lab.html', context)

@login_required(login_url='/login/')
def peminjaman_form_view(request, lab_pk):
    lab = get_object_or_404(Laboratorium, pk=lab_pk)
    if request.method == 'POST':
        form = PeminjamanForm(request.POST)
        if form.is_valid():
            peminjaman = form.save(commit=False)
            peminjaman.peminjam = request.user
            peminjaman.laboratorium = lab
            is_alat_baru_checked = request.POST.get('is_alat_baru_checkbox') == 'on'
            if is_alat_baru_checked:
                peminjaman.is_alat_baru = True
                peminjaman.status_peminjaman = 'Disetujui'
                peminjaman.nama_alat_baru = request.POST.get('nama_alat_baru')
                peminjaman.tipe_alat_baru = request.POST.get('tipe_alat_baru')
                peminjaman.sn_alat_baru = request.POST.get('sn_alat_baru')
                peminjaman.save()
                return render(request, 'laboratorium/sukses_versi_alat_baru.html', {'peminjaman': peminjaman})
            else:
                unit_alat_id = request.POST.get('unit_alat')
                if unit_alat_id:
                    peminjaman.unit_alat_id = unit_alat_id
                    peminjaman.is_alat_baru = False
                    peminjaman.save()
                    pesan = "Permintaan peminjaman Anda telah berhasil terkirim."
                    return render(request, 'laboratorium/sukses.html', {'pesan': pesan})
                else:
                    messages.error(request, "Anda wajib memilih unit alat yang tersedia.")
    else:
        form = PeminjamanForm()

    kategori_alat_list = KategoriUtama.objects.all().order_by('nama')
    jenis_alat_data = {}
    for ku in kategori_alat_list:
        jenis_alat_list = list(ku.sub_kategori.all().values('id', 'nama'))
        if jenis_alat_list:
            jenis_alat_data[ku.id] = jenis_alat_list
    unit_alat_data = {}
    for ka in KategoriAlat.objects.all():
        semua_unit = list(ka.unit_alat.all().values('id', 'tipe_atau_merk', 'serial_number', 'status'))
        if semua_unit:
            unit_alat_data[ka.id] = semua_unit
    context = {
        'form': form, 'lab': lab,
        'kategori_alat_list': kategori_alat_list,
        'jenis_alat_json': json.dumps(jenis_alat_data),
        'unit_alat_json': json.dumps(unit_alat_data),
    }
    return render(request, 'laboratorium/peminjaman_form.html', context)

@login_required(login_url='/login/')
def daftar_alat_view(request):
    kategori_list = KategoriUtama.objects.prefetch_related(
        'sub_kategori__unit_alat'
    ).filter(sub_kategori__unit_alat__isnull=False).distinct()

    context = {
        # Kirim data yang sudah terstruktur ini ke template
        'semua_kategori_utama': kategori_list
    }
    return render(request, 'laboratorium/daftar_alat.html', context)
    
@login_required(login_url='/login/')
def pengembalian_form_view(request, lab_pk):
    lab = get_object_or_404(Laboratorium, pk=lab_pk)
    if request.method == 'POST':
        form = PengembalianForm(request.POST, request.FILES, user=request.user, lab_pk=lab_pk)
        if form.is_valid():
            form.save()
            pesan_sukses = "Laporan pengembalian Anda telah berhasil terkirim."
            return render(request, 'laboratorium/sukses.html', {'pesan': pesan_sukses})
    else:
        form = PengembalianForm(user=request.user, lab_pk=lab_pk)
    context = {'lab': lab, 'form': form}
    return render(request, 'laboratorium/pengembalian_form.html', context)

def generate_loan_pdf(request, peminjaman_id):
    peminjaman = get_object_or_404(Peminjaman, pk=peminjaman_id)
    template_path = 'laboratorium/loan_ticket.html'
    context = {'peminjaman': peminjaman}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bukti-peminjaman-{peminjaman.nama_lengkap}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat membuat PDF: %s' % pisa_status.err)
    return response