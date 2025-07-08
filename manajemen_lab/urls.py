"""
URL configuration for manajemen_lab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# manajemen_lab/urls.py
from django.contrib import admin
from django.urls import path, include
# PASTIKAN DUA IMPORT INI ADA
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Teknologi Rekayasa Internet Laboratorium Administration"
admin.site.site_title = "Portal Admin Teknologi Rekayasa Internet Laboratorium"
admin.site.index_title = "Selamat Datang di Portal Administrasi Teknologi Rekayasa Internet Laboratorium"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('laboratorium.urls')), # Arahkan ke urls aplikasi
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
