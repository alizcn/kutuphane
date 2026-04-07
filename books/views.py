from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Kitap, Yazar, Kategori, UyeProfil, OduncAlma


def kitap_listesi(request):
    kategori_id = request.GET.get('kategori')
    kitaplar = Kitap.objects.select_related('yazar', 'kategori')
    if kategori_id:
        kitaplar = kitaplar.filter(kategori_id=kategori_id)
    kategoriler = Kategori.objects.all()
    return render(request, 'books/kitap_listesi.html', {
        'kitaplar': kitaplar,
        'kategoriler': kategoriler,
        'secili_kategori': int(kategori_id) if kategori_id else None,
    })


def kitap_detay(request, pk):
    kitap = get_object_or_404(Kitap.objects.select_related('yazar', 'kategori'), pk=pk)
    return render(request, 'books/kitap_detay.html', {'kitap': kitap})


def yazar_detay(request, pk):
    yazar = get_object_or_404(Yazar, pk=pk)
    kitaplar = yazar.kitaplar.select_related('kategori')
    return render(request, 'books/yazar_detay.html', {'yazar': yazar, 'kitaplar': kitaplar})


def dashboard(request):
    """Dashboard sayfası - Kütüphane istatistikleri ve özet bilgiler."""
    simdi = timezone.now()

    # --- Özet Kartlar ---
    toplam_kitap = Kitap.objects.count()
    toplam_yazar = Yazar.objects.count()
    toplam_uye = User.objects.filter(is_staff=False).count()
    aktif_odunc = OduncAlma.objects.filter(aktif=True).count()

    # --- En Çok Ödünç Alınan 5 Kitap ---
    populer_kitaplar = (
        Kitap.objects.annotate(odunc_sayisi=Count('odunc_islemleri'))
        .filter(odunc_sayisi__gt=0)
        .order_by('-odunc_sayisi')[:5]
    )

    # --- En Aktif 5 Üye ---
    aktif_uyeler = (
        User.objects.filter(is_staff=False)
        .annotate(odunc_sayisi=Count('odunc_islemleri'))
        .filter(odunc_sayisi__gt=0)
        .order_by('-odunc_sayisi')[:5]
    )

    # --- Kategorilere Göre Kitap Dağılımı ---
    kategori_dagilimi = (
        Kategori.objects.annotate(kitap_sayisi=Count('kitaplar'))
        .order_by('-kitap_sayisi')
    )

    # --- Aylık Ödünç Alma Trendi (Son 12 Ay) ---
    on_iki_ay_once = simdi - timedelta(days=365)
    aylik_islemler = (
        OduncAlma.objects.filter(odunc_tarihi__gte=on_iki_ay_once)
        .extra(select={
            'ay': "strftime('%%Y-%%m', odunc_tarihi)",
        })
        .values('ay')
        .annotate(sayi=Count('id'))
        .order_by('ay')
    )

    # Aylık trend verisini düzenle (son 12 ayı doldur)
    aylik_trend = []
    ay_map = {item['ay']: item['sayi'] for item in aylik_islemler}

    ay_isimleri = {
        1: 'Oca', 2: 'Şub', 3: 'Mar', 4: 'Nis',
        5: 'May', 6: 'Haz', 7: 'Tem', 8: 'Ağu',
        9: 'Eyl', 10: 'Eki', 11: 'Kas', 12: 'Ara',
    }

    for i in range(11, -1, -1):
        tarih = simdi - timedelta(days=i * 30)
        ay_key = tarih.strftime('%Y-%m')
        sayi = ay_map.get(ay_key, 0)
        ay_label = f"{ay_isimleri[tarih.month]} {tarih.year}"
        aylik_trend.append({
            'ay': ay_label,
            'ay_kisa': ay_isimleri[tarih.month],
            'sayi': sayi,
        })

    # Trend'deki maks değer (bar yükseklik oranı için)
    max_aylik = max((item['sayi'] for item in aylik_trend), default=1)
    if max_aylik == 0:
        max_aylik = 1

    for item in aylik_trend:
        item['oran'] = int((item['sayi'] / max_aylik) * 100)

    # --- Son İşlemler (Timeline) ---
    son_islemler = (
        OduncAlma.objects.select_related('uye', 'kitap')
        .order_by('-odunc_tarihi')[:15]
    )

    context = {
        'toplam_kitap': toplam_kitap,
        'toplam_yazar': toplam_yazar,
        'toplam_uye': toplam_uye,
        'aktif_odunc': aktif_odunc,
        'populer_kitaplar': populer_kitaplar,
        'aktif_uyeler': aktif_uyeler,
        'kategori_dagilimi': kategori_dagilimi,
        'aylik_trend': aylik_trend,
        'max_aylik': max_aylik,
        'son_islemler': son_islemler,
    }
    return render(request, 'books/dashboard.html', context)
