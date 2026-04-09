"""
Veri Migrasyonu: Takas sistemi icin ornek (mock) kullanici, kitap ve teklif verileri.
"""
from django.db import migrations
from django.contrib.auth.hashers import make_password


def takas_mock_veri_olustur(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UyeProfil = apps.get_model('books', 'UyeProfil')
    KullaniciKitap = apps.get_model('books', 'KullaniciKitap')
    TakasTeklifi = apps.get_model('books', 'TakasTeklifi')

    kullanici_verileri = [
        {'username': 'ayse_kitapsever', 'first_name': 'Ayse',   'last_name': 'Kaya',   'email': 'ayse@example.com'},
        {'username': 'mehmet_okur',     'first_name': 'Mehmet', 'last_name': 'Demir',  'email': 'mehmet@example.com'},
        {'username': 'zeynep_yazar',    'first_name': 'Zeynep', 'last_name': 'Celik',  'email': 'zeynep@example.com'},
        {'username': 'ali_okuyucu',     'first_name': 'Ali',    'last_name': 'Arslan', 'email': 'ali@example.com'},
    ]

    kullanicilar = {}
    for veri in kullanici_verileri:
        kullanici, olusturuldu = User.objects.get_or_create(
            username=veri['username'],
            defaults={
                'first_name': veri['first_name'],
                'last_name':  veri['last_name'],
                'email':      veri['email'],
                'password':   make_password('takas1234'),
            },
        )
        if olusturuldu:
            kullanici.password = make_password('takas1234')
            kullanici.save()
        kullanicilar[veri['username']] = kullanici
        UyeProfil.objects.get_or_create(kullanici=kullanici, defaults={'telefon': '', 'adres': ''})

    ayse   = kullanicilar['ayse_kitapsever']
    mehmet = kullanicilar['mehmet_okur']
    zeynep = kullanicilar['zeynep_yazar']
    ali    = kullanicilar['ali_okuyucu']

    # ── Ayse'nin kitaplari ──
    ayse_k1 = KullaniciKitap.objects.create(
        sahip=ayse, kitap_adi='Donusum', yazar_adi='Franz Kafka',
        aciklama='Cok iyi kosulda, bir kez okundu. Harika bir klasik.',
        durum='musait',
    )
    ayse_k2 = KullaniciKitap.objects.create(
        sahip=ayse, kitap_adi='1984', yazar_adi='George Orwell',
        aciklama='Az kullanilmis, kapak biraz soluk. Distopya severler icin.',
        durum='musait',
    )
    ayse_k3 = KullaniciKitap.objects.create(
        sahip=ayse, kitap_adi='Simyaci', yazar_adi='Paulo Coelho',
        aciklama='Mukemmel kosul, hediye olarak alinmisti.',
        durum='takasta',
    )

    # ── Mehmet'in kitaplari ──
    mehmet_k1 = KullaniciKitap.objects.create(
        sahip=mehmet, kitap_adi='Suc ve Ceza', yazar_adi='Fyodor Dostoyevski',
        aciklama='Iyi kosulda, eski baski ama okunabilir durumda.',
        durum='musait',
    )
    mehmet_k2 = KullaniciKitap.objects.create(
        sahip=mehmet, kitap_adi='Beyaz Dis', yazar_adi='Jack London',
        aciklama='Yeni gibi, hic okunmamis.',
        durum='musait',
    )
    mehmet_k3 = KullaniciKitap.objects.create(  # noqa: F841
        sahip=mehmet, kitap_adi='Marti', yazar_adi='Richard Bach',
        aciklama='Kucuk boyut, harika bir kitap. Sayfalar sararmis.',
        durum='musait',
    )

    # ── Zeynep'in kitaplari ──
    zeynep_k1 = KullaniciKitap.objects.create(
        sahip=zeynep, kitap_adi='Kucuk Prens', yazar_adi='Antoine de Saint-Exupery',
        aciklama='Renkli baski, cok iyi kosulda.',
        durum='musait',
    )
    zeynep_k2 = KullaniciKitap.objects.create(
        sahip=zeynep, kitap_adi='Anna Karenina', yazar_adi='Lev Tolstoy',
        aciklama='Kalin ama deger, biraz okunmus.',
        durum='musait',
    )

    # ── Ali'nin kitaplari ──
    ali_k1 = KullaniciKitap.objects.create(
        sahip=ali, kitap_adi='Sefiller', yazar_adi='Victor Hugo',
        aciklama='2 cilt, her ikisi de mevcut ve iyi kosulda.',
        durum='musait',
    )
    ali_k2 = KullaniciKitap.objects.create(
        sahip=ali, kitap_adi='Bulbulu Oldurrmek', yazar_adi='Harper Lee',
        aciklama='Az kullanilmis, temiz.',
        durum='musait',
    )

    # ── Takas Teklifleri ──

    # Mehmet → Ayse: "Suc ve Ceza" karsiliginda "Donusum" istiyor — BEKLEMEDE
    TakasTeklifi.objects.create(
        gonderen=mehmet, alici=ayse,
        teklif_edilen_kitap=mehmet_k1,
        istenen_kitap=ayse_k1,
        mesaj='Merhaba Ayse Hanim, Kafka\'nin Donusum\'unu merak ediyorum. '
              'Karsiliginda Dostoyevski\'nin Suc ve Ceza\'sini sunabilirim.',
        durum='beklemede',
    )

    # Zeynep → Mehmet: "Kucuk Prens" karsiliginda "Beyaz Dis" istiyor — BEKLEMEDE
    TakasTeklifi.objects.create(
        gonderen=zeynep, alici=mehmet,
        teklif_edilen_kitap=zeynep_k1,
        istenen_kitap=mehmet_k2,
        mesaj='Merhaba! Beyaz Dis cok guzel bir kitap, okumak istiyorum. '
              'Kucuk Prens\'i oneririm, renkli baski.',
        durum='beklemede',
    )

    # Ali → Ayse: "Sefiller" karsiliginda "1984" istiyor — ONAYLANDI
    TakasTeklifi.objects.create(
        gonderen=ali, alici=ayse,
        teklif_edilen_kitap=ali_k1,
        istenen_kitap=ayse_k2,
        mesaj='Orwell\'in 1984\'unu okumak istiyorum, Sefiller ile takas yapalim mi?',
        durum='onaylandi',
    )

    # Ali → Ayse: "Bulbulu Oldurrmek" karsiliginda "Simyaci" istiyor — ONAYLANDI
    TakasTeklifi.objects.create(
        gonderen=ali, alici=ayse,
        teklif_edilen_kitap=ali_k2,
        istenen_kitap=ayse_k3,
        mesaj='Simyaci\'yi cok duymak istedim, Bulbulu Oldurrmek ile degisir misiniz?',
        durum='onaylandi',
    )

    # Zeynep → Ayse: "Anna Karenina" karsiliginda "Donusum" istiyor — REDDEDILDI
    TakasTeklifi.objects.create(
        gonderen=zeynep, alici=ayse,
        teklif_edilen_kitap=zeynep_k2,
        istenen_kitap=ayse_k1,
        mesaj='Donusum\'u cok istedim ama anliyorum zaten baska teklifler var.',
        durum='reddedildi',
    )


def takas_mock_veri_sil(apps, schema_editor):
    """Geri alma (reverse) migrasyonu icin verileri temizle."""
    User = apps.get_model('auth', 'User')
    mock_kullanicilar = ['ayse_kitapsever', 'mehmet_okur', 'zeynep_yazar', 'ali_okuyucu']
    User.objects.filter(username__in=mock_kullanicilar).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_kullanicikitap_takasteklifi'),
    ]

    operations = [
        migrations.RunPython(
            takas_mock_veri_olustur,
            reverse_code=takas_mock_veri_sil,
        ),
    ]
