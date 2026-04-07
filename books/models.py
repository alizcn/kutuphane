from django.db import models


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
