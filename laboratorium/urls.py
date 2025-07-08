# laboratorium/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard_view, name='dashboard'),
    path('lab/<int:lab_pk>/', views.lab_detail_view, name='lab_detail'),
    path('lab/<int:lab_pk>/pinjam/', views.peminjaman_form_view, name='peminjaman_form'),
    path('lab/<int:lab_pk>/kembalikan/', views.pengembalian_form_view, name='pengembalian_form'),
    path('peminjaman/pdf/<int:peminjaman_id>/', views.generate_loan_pdf, name='generate_loan_pdf'),
    path('lab/<int:lab_pk>/deskripsi/', views.deskripsi_lab_view, name='deskripsi_lab'),
    path('daftar-alat/', views.daftar_alat_view, name='daftar_alat'),
]