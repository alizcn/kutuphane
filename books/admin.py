from django.contrib import admin
from .models import Yazar, Kategori, Kitap, UyeProfil, OduncAlma, KitapDegerlendirme


@admin.register(Yazar)
class YazarAdmin(admin.ModelAdmin):
    list_display = ('ad', 'dogum_yili')
    search_fields = ('ad',)


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad',)
    search_fields = ('ad',)


@admin.register(Kitap)
class KitapAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yazar', 'kategori', 'yayin_yili', 'stok')
    list_filter = ('kategori', 'yazar')
    search_fields = ('baslik', 'yazar__ad')


@admin.register(UyeProfil)
class UyeProfilAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'telefon')
    search_fields = ('kullanici__username', 'kullanici__first_name', 'kullanici__last_name')


@admin.register(OduncAlma)
class OduncAlmaAdmin(admin.ModelAdmin):
    list_display = ('uye', 'kitap', 'odunc_tarihi', 'son_iade_tarihi', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('uye__username', 'kitap__baslik')
    raw_id_fields = ('uye', 'kitap')


@admin.register(KitapDegerlendirme)
class KitapDegerlendirmeAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'kitap', 'puan', 'olusturma_tarihi')
    list_filter = ('puan',)
    search_fields = ('kullanici__username', 'kitap__baslik', 'yorum')
    raw_id_fields = ('kullanici', 'kitap')
    readonly_fields = ('olusturma_tarihi',)
