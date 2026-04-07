from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


ODUNC_SURESI_GUN = 15


class Yazar(models.Model):
    ad = models.CharField(max_length=100)
    biyografi = models.TextField(blank=True)
    dogum_yili = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Yazar'
        verbose_name_plural = 'Yazarlar'
        ordering = ['ad']

    def __str__(self):
        return self.ad


class Kategori(models.Model):
    ad = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['ad']

    def __str__(self):
        return self.ad


class Kitap(models.Model):
    baslik = models.CharField(max_length=200)
    yazar = models.ForeignKey(Yazar, on_delete=models.CASCADE, related_name='kitaplar')
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, related_name='kitaplar')
    yayin_yili = models.PositiveIntegerField()
    sayfa_sayisi = models.PositiveIntegerField()
    aciklama = models.TextField(blank=True)
    stok = models.PositiveIntegerField(default=0)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kitap'
        verbose_name_plural = 'Kitaplar'
        ordering = ['-olusturma_tarihi']

    def __str__(self):
        return f"{self.baslik} - {self.yazar.ad}"

    @property
    def musait_mi(self):
        return self.stok > 0


class UyeProfili(models.Model):
    kullanici = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telefon = models.CharField(max_length=15, blank=True)
    adres = models.TextField(blank=True)
    kayit_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Üye Profili'
        verbose_name_plural = 'Üye Profilleri'

    def __str__(self):
        return f"{self.kullanici.get_full_name() or self.kullanici.username}"


class OduncAlma(models.Model):
    uye = models.ForeignKey(User, on_delete=models.CASCADE, related_name='odunc_almalar')
    kitap = models.ForeignKey(Kitap, on_delete=models.CASCADE, related_name='odunc_almalar')
    odunc_tarihi = models.DateTimeField(default=timezone.now)
    son_iade_tarihi = models.DateTimeField()
    iade_tarihi = models.DateTimeField(null=True, blank=True)
    iade_edildi = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ödünç Alma'
        verbose_name_plural = 'Ödünç Almalar'
        ordering = ['-odunc_tarihi']

    def __str__(self):
        durum = 'İade edildi' if self.iade_edildi else 'Ödünç'
        return f"{self.uye.get_full_name()} - {self.kitap.baslik} ({durum})"

    def save(self, *args, **kwargs):
        if not self.son_iade_tarihi:
            self.son_iade_tarihi = self.odunc_tarihi + timedelta(days=ODUNC_SURESI_GUN)
        super().save(*args, **kwargs)

    @property
    def gecikme_var_mi(self):
        if self.iade_edildi:
            return self.iade_tarihi and self.iade_tarihi > self.son_iade_tarihi
        return timezone.now() > self.son_iade_tarihi

    @property
    def kalan_gun(self):
        if self.iade_edildi:
            return 0
        delta = self.son_iade_tarihi - timezone.now()
        return delta.days

    @property
    def gecikme_gun(self):
        if not self.gecikme_var_mi:
            return 0
        if self.iade_edildi and self.iade_tarihi:
            delta = self.iade_tarihi - self.son_iade_tarihi
        else:
            delta = timezone.now() - self.son_iade_tarihi
        return max(delta.days, 0)
