from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Yazar, Kategori, Kitap, UyeProfil, OduncAlma


class YazarSerializer(serializers.ModelSerializer):
    kitap_sayisi = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Yazar
        fields = ['id', 'ad', 'biyografi', 'dogum_yili', 'kitap_sayisi']

    def get_fields(self):
        fields = super().get_fields()
        if 'kitap_sayisi' in fields and not hasattr(self.instance, 'kitap_sayisi'):
            # annotate edilmemişse alanı kaldır
            if self.instance is not None:
                fields.pop('kitap_sayisi', None)
        return fields


class KategoriSerializer(serializers.ModelSerializer):
    kitap_sayisi = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Kategori
        fields = ['id', 'ad', 'kitap_sayisi']


class KitapSerializer(serializers.ModelSerializer):
    yazar_ad = serializers.CharField(source='yazar.ad', read_only=True)
    kategori_ad = serializers.CharField(source='kategori.ad', read_only=True, default=None)
    odunc_alinabilir = serializers.BooleanField(read_only=True)

    class Meta:
        model = Kitap
        fields = [
            'id', 'baslik', 'yazar', 'yazar_ad', 'kategori', 'kategori_ad',
            'yayin_yili', 'sayfa_sayisi', 'aciklama', 'stok',
            'odunc_alinabilir', 'olusturma_tarihi',
        ]
        read_only_fields = ['olusturma_tarihi']


class UyeProfilSerializer(serializers.ModelSerializer):
    kullanici_adi = serializers.CharField(source='kullanici.username', read_only=True)
    ad_soyad = serializers.SerializerMethodField()

    class Meta:
        model = UyeProfil
        fields = ['id', 'kullanici', 'kullanici_adi', 'ad_soyad', 'telefon', 'adres']
        read_only_fields = ['kullanici']

    def get_ad_soyad(self, obj):
        return obj.kullanici.get_full_name() or obj.kullanici.username


class OduncAlmaSerializer(serializers.ModelSerializer):
    uye_ad = serializers.CharField(source='uye.get_full_name', read_only=True)
    kitap_baslik = serializers.CharField(source='kitap.baslik', read_only=True)
    gecikme_var = serializers.BooleanField(read_only=True)
    gecikme_gun = serializers.IntegerField(read_only=True)
    kalan_gun = serializers.IntegerField(read_only=True)

    class Meta:
        model = OduncAlma
        fields = [
            'id', 'uye', 'uye_ad', 'kitap', 'kitap_baslik',
            'odunc_tarihi', 'son_iade_tarihi', 'teslim_tarihi',
            'aktif', 'gecikme_var', 'gecikme_gun', 'kalan_gun',
        ]
        read_only_fields = ['odunc_tarihi', 'son_iade_tarihi', 'teslim_tarihi', 'aktif']
