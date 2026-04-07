from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from .models import Kitap, Yazar, Kategori, UyeProfil, OduncAlma, ODUNC_SURESI_GUN
from .forms import KayitFormu, GirisFormu, ProfilFormu, OduncAlmaFormu


# ──────────────────────────────────────────────
# Kitap View'lari
# ──────────────────────────────────────────────

def kitap_listesi(request):
    kategori_id = request.GET.get('kategori')
    arama = request.GET.get('q', '').strip()

    kitaplar = Kitap.objects.select_related('yazar', 'kategori')

    if kategori_id:
        kitaplar = kitaplar.filter(kategori_id=kategori_id)

    if arama:
        kitaplar = kitaplar.filter(
            Q(baslik__icontains=arama) |
            Q(yazar__ad__icontains=arama) |
            Q(aciklama__icontains=arama)
        )

    kategoriler = Kategori.objects.all()

    return render(request, 'books/kitap_listesi.html', {
        'kitaplar': kitaplar,
        'kategoriler': kategoriler,
        'secili_kategori': int(kategori_id) if kategori_id else None,
        'arama': arama,
    })


def kitap_detay(request, pk):
    kitap = get_object_or_404(
        Kitap.objects.select_related('yazar', 'kategori'), pk=pk
    )
    return render(request, 'books/kitap_detay.html', {'kitap': kitap})


def yazar_detay(request, pk):
    yazar = get_object_or_404(Yazar, pk=pk)
    kitaplar = yazar.kitaplar.select_related('kategori')
    return render(request, 'books/yazar_detay.html', {
        'yazar': yazar,
        'kitaplar': kitaplar,
    })


# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────

def dashboard(request):
    """Dashboard sayfasi - Kutuphane istatistikleri ve ozet bilgiler."""
    simdi = timezone.now()

    # --- Ozet Kartlar ---
    toplam_kitap = Kitap.objects.count()
    toplam_yazar = Yazar.objects.count()
    toplam_uye = User.objects.filter(is_staff=False).count()
    aktif_odunc = OduncAlma.objects.filter(aktif=True).count()
    geciken_odunc = OduncAlma.objects.filter(
        aktif=True, son_iade_tarihi__lt=simdi
    ).count()

    # --- En Cok Odunc Alinan 5 Kitap ---
    populer_kitaplar = (
        Kitap.objects.annotate(odunc_sayisi=Count('odunc_islemleri'))
        .filter(odunc_sayisi__gt=0)
        .order_by('-odunc_sayisi')[:5]
    )

    # --- En Aktif 5 Uye ---
    aktif_uyeler = (
        User.objects.filter(is_staff=False)
        .annotate(odunc_sayisi=Count('odunc_islemleri'))
        .filter(odunc_sayisi__gt=0)
        .order_by('-odunc_sayisi')[:5]
    )

    # --- Kategorilere Gore Kitap Dagilimi ---
    kategori_dagilimi = (
        Kategori.objects.annotate(kitap_sayisi=Count('kitaplar'))
        .order_by('-kitap_sayisi')
    )

    # --- Aylik Odunc Alma Trendi (Son 12 Ay) ---
    on_iki_ay_once = simdi - timedelta(days=365)
    aylik_islemler = (
        OduncAlma.objects.filter(odunc_tarihi__gte=on_iki_ay_once)
        .annotate(ay=TruncMonth('odunc_tarihi'))
        .values('ay')
        .annotate(sayi=Count('id'))
        .order_by('ay')
    )

    # Aylik trend verisini duzenle (son 12 ayi doldur)
    aylik_trend = []
    ay_map = {}
    for item in aylik_islemler:
        key = item['ay'].strftime('%Y-%m')
        ay_map[key] = item['sayi']

    ay_isimleri = {
        1: 'Oca', 2: 'Sub', 3: 'Mar', 4: 'Nis',
        5: 'May', 6: 'Haz', 7: 'Tem', 8: 'Agu',
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

    # Trend'deki maks deger (bar yukseklik orani icin)
    max_aylik = max((item['sayi'] for item in aylik_trend), default=1)
    if max_aylik == 0:
        max_aylik = 1

    for item in aylik_trend:
        item['oran'] = int((item['sayi'] / max_aylik) * 100)

    # --- Son Islemler (Timeline) ---
    son_islemler = (
        OduncAlma.objects.select_related('uye', 'kitap')
        .order_by('-odunc_tarihi')[:15]
    )

    context = {
        'toplam_kitap': toplam_kitap,
        'toplam_yazar': toplam_yazar,
        'toplam_uye': toplam_uye,
        'aktif_odunc': aktif_odunc,
        'geciken_odunc': geciken_odunc,
        'populer_kitaplar': populer_kitaplar,
        'aktif_uyeler': aktif_uyeler,
        'kategori_dagilimi': kategori_dagilimi,
        'aylik_trend': aylik_trend,
        'max_aylik': max_aylik,
        'son_islemler': son_islemler,
    }
    return render(request, 'books/dashboard.html', context)


# ──────────────────────────────────────────────
# Kimlik Dogrulama (Auth) View'lari
# ──────────────────────────────────────────────

def kayit_view(request):
    if request.user.is_authenticated:
        return redirect('books:kitap_listesi')

    if request.method == 'POST':
        form = KayitFormu(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Kaydiniz basariyla olusturuldu!')
            return redirect('books:kitap_listesi')
    else:
        form = KayitFormu()

    return render(request, 'books/kayit.html', {'form': form})


def giris_view(request):
    if request.user.is_authenticated:
        return redirect('books:kitap_listesi')

    if request.method == 'POST':
        form = GirisFormu(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Basariyla giris yaptiniz!')
            next_url = request.GET.get('next', 'books:kitap_listesi')
            return redirect(next_url)
    else:
        form = GirisFormu()

    return render(request, 'books/giris.html', {'form': form})


def cikis_view(request):
    logout(request)
    messages.info(request, 'Basariyla cikis yaptiniz.')
    return redirect('books:kitap_listesi')


@login_required
def profil_view(request):
    profil, created = UyeProfil.objects.get_or_create(
        kullanici=request.user,
        defaults={'telefon': '', 'adres': ''},
    )

    if request.method == 'POST':
        form = ProfilFormu(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz guncellendi!')
            return redirect('books:profil')
    else:
        form = ProfilFormu(instance=profil)

    # Kullanicinin odunc islemleri
    aktif_oduncler = OduncAlma.objects.filter(
        uye=request.user, aktif=True
    ).select_related('kitap')
    gecmis_oduncler = OduncAlma.objects.filter(
        uye=request.user, aktif=False
    ).select_related('kitap').order_by('-teslim_tarihi')[:10]

    return render(request, 'books/profil.html', {
        'form': form,
        'profil': profil,
        'aktif_oduncler': aktif_oduncler,
        'gecmis_oduncler': gecmis_oduncler,
    })


# ──────────────────────────────────────────────
# Odunc Alma / Iade View'lari
# ──────────────────────────────────────────────

@login_required
def odunc_al(request, pk):
    kitap = get_object_or_404(Kitap, pk=pk)

    if request.method == 'POST':
        form = OduncAlmaFormu(request.POST)
        if form.is_valid():
            # Zaten bu kitabi odunc almis mi kontrol et
            zaten_odunc = OduncAlma.objects.filter(
                uye=request.user, kitap=kitap, aktif=True
            ).exists()
            if zaten_odunc:
                messages.warning(request, 'Bu kitabi zaten odunc almissiniz.')
                return redirect('books:kitap_detay', pk=kitap.pk)

            if kitap.stok <= 0:
                messages.error(request, 'Bu kitap stokta bulunmuyor.')
                return redirect('books:kitap_detay', pk=kitap.pk)

            # Odunc alma islemi
            OduncAlma.objects.create(
                uye=request.user,
                kitap=kitap,
            )
            kitap.stok -= 1
            kitap.save()
            messages.success(
                request,
                f'"{kitap.baslik}" basariyla odunc alindi. '
                f'{ODUNC_SURESI_GUN} gun icinde iade etmeniz gerekmektedir.'
            )
            return redirect('books:profil')
    else:
        form = OduncAlmaFormu(initial={'kitap_id': kitap.pk})

    return render(request, 'books/odunc_al.html', {
        'kitap': kitap,
        'form': form,
    })


@login_required
def iade_et(request, pk):
    odunc = get_object_or_404(
        OduncAlma, pk=pk, uye=request.user, aktif=True
    )

    if request.method == 'POST':
        odunc.aktif = False
        odunc.teslim_tarihi = timezone.now()
        odunc.save()

        odunc.kitap.stok += 1
        odunc.kitap.save()

        messages.success(
            request,
            f'"{odunc.kitap.baslik}" basariyla iade edildi.'
        )
        return redirect('books:profil')

    return render(request, 'books/iade_et.html', {'odunc': odunc})
