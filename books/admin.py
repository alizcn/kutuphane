from django.contrib import admin
from .models import Yazar, Kategori, Kitap


@admin.register(Yazar)
class YazarAdmin(admin.ModelAdmin):
    list_display = ('ad', 'dogum_yili')
    search_fields = ('ad',)


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad',)


@admin.register(Kitap)
class KitapAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yazar', 'kategori', 'yayin_yili', 'stok')
    list_filter = ('kategori', 'yazar')
    search_fields = ('baslik',)
