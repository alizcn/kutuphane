from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator


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
    def odunc_alinabilir(self):
        return self.stok > 0

    @property
    def ortalama_puan(self):
        sonuc = self.degerlendirmeler.aggregate(Avg('puan'))
        val = sonuc['puan__avg']
        return round(val, 1) if val is not None else None

    @property
    def degerlendirme_sayisi(self):
        return self.degerlendirmeler.count()


class UyeProfil(models.Model):
    kullanici = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telefon = models.CharField(max_length=15, blank=True)
    adres = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Üye Profili'
        verbose_name_plural = 'Üye Profilleri'

    def __str__(self):
        return f"{self.kullanici.get_full_name() or self.kullanici.username}"

    @property
    def aktif_odunc_sayisi(self):
        return self.kullanici.odunc_islemleri.filter(aktif=True).count()


ODUNC_SURESI_GUN = 15


class OduncAlma(models.Model):
    uye = models.ForeignKey(User, on_delete=models.CASCADE, related_name='odunc_islemleri')
    kitap = models.ForeignKey(Kitap, on_delete=models.CASCADE, related_name='odunc_islemleri')
    odunc_tarihi = models.DateTimeField(default=timezone.now)
    son_iade_tarihi = models.DateTimeField()
    teslim_tarihi = models.DateTimeField(null=True, blank=True)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ödünç Alma'
        verbose_name_plural = 'Ödünç Alma İşlemleri'
        ordering = ['-odunc_tarihi']

    def __str__(self):
        durum = 'Aktif' if self.aktif else 'İade Edildi'
        return f"{self.uye.get_full_name()} - {self.kitap.baslik} ({durum})"

    def save(self, *args, **kwargs):
        if not self.son_iade_tarihi:
            self.son_iade_tarihi = self.odunc_tarihi + timedelta(days=ODUNC_SURESI_GUN)
        super().save(*args, **kwargs)

    @property
    def gecikme_var(self):
        if self.aktif:
            return timezone.now() > self.son_iade_tarihi
        return False

    @property
    def gecikme_gun(self):
        if self.gecikme_var:
            delta = timezone.now() - self.son_iade_tarihi
            return delta.days
        return 0

    @property
    def kalan_gun(self):
        if self.aktif and not self.gecikme_var:
            delta = self.son_iade_tarihi - timezone.now()
            return delta.days
        return 0


class KitapDegerlendirme(models.Model):
    PUAN_SECENEKLERI = [
        (1, '1 Yildiz'),
        (2, '2 Yildiz'),
        (3, '3 Yildiz'),
        (4, '4 Yildiz'),
        (5, '5 Yildiz'),
    ]

    kullanici = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='degerlendirmeler'
    )
    kitap = models.ForeignKey(
        Kitap, on_delete=models.CASCADE, related_name='degerlendirmeler'
    )
    puan = models.PositiveSmallIntegerField(
        choices=PUAN_SECENEKLERI,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    yorum = models.TextField(blank=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kitap Değerlendirmesi'
        verbose_name_plural = 'Kitap Değerlendirmeleri'
        ordering = ['-olusturma_tarihi']
        constraints = [
            models.UniqueConstraint(
                fields=['kullanici', 'kitap'],
                name='unique_kullanici_kitap_degerlendirme',
            )
        ]

    def __str__(self):
        return f"{self.kullanici.username} - {self.kitap.baslik} ({self.puan}/5)"


# ──────────────────────────────────────────────
# Takas Sistemi
# ──────────────────────────────────────────────

class KullaniciKitap(models.Model):
    """Kullanıcının takasa açmak istediği kendi kitabı."""

    DURUM_SECENEKLERI = [
        ('musait', 'Müsait'),
        ('takasta', 'Takasta'),
        ('kaldirildi', 'Kaldırıldı'),
    ]

    sahip = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='kullanici_kitaplari'
    )
    kitap_adi = models.CharField(max_length=200, verbose_name='Kitap Adı')
    yazar_adi = models.CharField(max_length=100, verbose_name='Yazar Adı')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama / Durum Notu')
    durum = models.CharField(
        max_length=20, choices=DURUM_SECENEKLERI, default='musait', verbose_name='Durum'
    )
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kullanıcı Kitabı'
        verbose_name_plural = 'Kullanıcı Kitapları'
        ordering = ['-olusturma_tarihi']

    def __str__(self):
        return f"{self.kitap_adi} ({self.sahip.username})"

    @property
    def bekleyen_teklif_sayisi(self):
        """Bu kitaba gelen bekleyen teklif sayısı."""
        return self.gelen_teklifler.filter(durum='beklemede').count()

    @property
    def musait_mi(self):
        return self.durum == 'musait'


class TakasTeklifi(models.Model):
    """İki kullanıcı arasındaki takas teklifi."""

    DURUM_SECENEKLERI = [
        ('beklemede', 'Beklemede'),
        ('onaylandi', 'Onaylandı'),
        ('reddedildi', 'Reddedildi'),
        ('iptal', 'İptal Edildi'),
    ]

    gonderen = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='gonderilen_teklifler'
    )
    alici = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='alinan_teklifler'
    )
    # Gönderenin teklif ettiği kendi kitabı
    teklif_edilen_kitap = models.ForeignKey(
        KullaniciKitap, on_delete=models.CASCADE, related_name='verilen_teklifler'
    )
    # Gönderenin almak istediği, alıcıya ait kitap
    istenen_kitap = models.ForeignKey(
        KullaniciKitap, on_delete=models.CASCADE, related_name='gelen_teklifler'
    )
    mesaj = models.TextField(blank=True, verbose_name='Mesaj')
    durum = models.CharField(
        max_length=20, choices=DURUM_SECENEKLERI, default='beklemede', verbose_name='Durum'
    )
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Takas Teklifi'
        verbose_name_plural = 'Takas Teklifleri'
        ordering = ['-olusturma_tarihi']

    def __str__(self):
        return (
            f"{self.gonderen.username} → {self.alici.username}: "
            f"{self.teklif_edilen_kitap.kitap_adi} ↔ {self.istenen_kitap.kitap_adi}"
        )

    @property
    def beklemede_mi(self):
        return self.durum == 'beklemede'
