from django.shortcuts import render, get_object_or_404
from .models import Kitap, Yazar, Kategori


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
