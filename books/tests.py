from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import (
    Yazar, Kategori, Kitap, UyeProfil, OduncAlma,
    KitapDegerlendirme, ODUNC_SURESI_GUN,
)
from .forms import KayitFormu, DegerlendirmeFormu, OduncAlmaFormu, ProfilFormu


# ──────────────────────────────────────────────
# Model Testleri
# ──────────────────────────────────────────────

class YazarModelTest(TestCase):
    def test_str(self):
        yazar = Yazar.objects.create(ad='Test Yazar', dogum_yili=1980)
        self.assertEqual(str(yazar), 'Test Yazar')

    def test_ordering(self):
        Yazar.objects.create(ad='Zeynep')
        Yazar.objects.create(ad='Ali')
        yazarlar = list(Yazar.objects.values_list('ad', flat=True))
        self.assertEqual(yazarlar, ['Ali', 'Zeynep'])


class KategoriModelTest(TestCase):
    def test_str(self):
        kat = Kategori.objects.create(ad='Roman')
        self.assertEqual(str(kat), 'Roman')

    def test_unique_ad(self):
        Kategori.objects.create(ad='Roman')
        with self.assertRaises(Exception):
            Kategori.objects.create(ad='Roman')


class KitapModelTest(TestCase):
    def setUp(self):
        self.yazar = Yazar.objects.create(ad='Yazar A', dogum_yili=1970)
        self.kategori = Kategori.objects.create(ad='Roman')
        self.kitap = Kitap.objects.create(
            baslik='Test Kitap',
            yazar=self.yazar,
            kategori=self.kategori,
            yayin_yili=2020,
            sayfa_sayisi=300,
            stok=5,
        )

    def test_str(self):
        self.assertEqual(str(self.kitap), 'Test Kitap - Yazar A')

    def test_odunc_alinabilir_true(self):
        self.assertTrue(self.kitap.odunc_alinabilir)

    def test_odunc_alinabilir_false(self):
        self.kitap.stok = 0
        self.kitap.save()
        self.assertFalse(self.kitap.odunc_alinabilir)

    def test_ortalama_puan_none(self):
        """Degerlendirme yokken ortalama_puan None olmali."""
        self.assertIsNone(self.kitap.ortalama_puan)

    def test_ortalama_puan_hesaplama(self):
        user1 = User.objects.create_user('u1', password='pass1234')
        user2 = User.objects.create_user('u2', password='pass1234')
        KitapDegerlendirme.objects.create(kullanici=user1, kitap=self.kitap, puan=4)
        KitapDegerlendirme.objects.create(kullanici=user2, kitap=self.kitap, puan=2)
        self.assertEqual(self.kitap.ortalama_puan, 3.0)

    def test_degerlendirme_sayisi(self):
        user = User.objects.create_user('u1', password='pass1234')
        self.assertEqual(self.kitap.degerlendirme_sayisi, 0)
        KitapDegerlendirme.objects.create(kullanici=user, kitap=self.kitap, puan=5)
        self.assertEqual(self.kitap.degerlendirme_sayisi, 1)


class UyeProfilModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', password='pass1234', first_name='Ali', last_name='Veli',
        )
        self.profil = UyeProfil.objects.create(kullanici=self.user)

    def test_str(self):
        self.assertEqual(str(self.profil), 'Ali Veli')

    def test_str_no_fullname(self):
        user2 = User.objects.create_user('noname', password='pass1234')
        profil2 = UyeProfil.objects.create(kullanici=user2)
        self.assertEqual(str(profil2), 'noname')

    def test_aktif_odunc_sayisi(self):
        self.assertEqual(self.profil.aktif_odunc_sayisi, 0)


class OduncAlmaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Kitap', yazar=self.yazar, yayin_yili=2020,
            sayfa_sayisi=200, stok=3,
        )

    def test_son_iade_tarihi_auto(self):
        """son_iade_tarihi verilmezse otomatik hesaplaniyor mu?"""
        odunc = OduncAlma(uye=self.user, kitap=self.kitap)
        odunc.save()
        beklenen = odunc.odunc_tarihi + timedelta(days=ODUNC_SURESI_GUN)
        self.assertAlmostEqual(
            odunc.son_iade_tarihi.timestamp(),
            beklenen.timestamp(),
            delta=2,
        )

    def test_str_aktif(self):
        odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        self.assertIn('Aktif', str(odunc))

    def test_str_iade(self):
        odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap, aktif=False)
        # Model Turkce karakter kullaniyor: 'İade Edildi'
        self.assertIn('\u0130ade Edildi', str(odunc))

    def test_gecikme_yok(self):
        odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        self.assertFalse(odunc.gecikme_var)
        self.assertEqual(odunc.gecikme_gun, 0)

    def test_gecikme_var(self):
        odunc = OduncAlma.objects.create(
            uye=self.user,
            kitap=self.kitap,
            son_iade_tarihi=timezone.now() - timedelta(days=5),
        )
        self.assertTrue(odunc.gecikme_var)
        self.assertGreaterEqual(odunc.gecikme_gun, 4)

    def test_kalan_gun(self):
        odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        self.assertGreater(odunc.kalan_gun, 0)

    def test_kalan_gun_gecikme_durumunda_sifir(self):
        odunc = OduncAlma.objects.create(
            uye=self.user,
            kitap=self.kitap,
            son_iade_tarihi=timezone.now() - timedelta(days=1),
        )
        self.assertEqual(odunc.kalan_gun, 0)


class KitapDegerlendirmeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Kitap', yazar=self.yazar, yayin_yili=2020,
            sayfa_sayisi=200, stok=3,
        )

    def test_str(self):
        d = KitapDegerlendirme.objects.create(
            kullanici=self.user, kitap=self.kitap, puan=4,
        )
        self.assertIn('4/5', str(d))

    def test_unique_constraint(self):
        """Ayni kullanici ayni kitabi iki kez degerlendirememeli."""
        KitapDegerlendirme.objects.create(
            kullanici=self.user, kitap=self.kitap, puan=3,
        )
        with self.assertRaises(Exception):
            KitapDegerlendirme.objects.create(
                kullanici=self.user, kitap=self.kitap, puan=5,
            )


# ──────────────────────────────────────────────
# Form Testleri
# ──────────────────────────────────────────────

class KayitFormuTest(TestCase):
    def test_valid_form(self):
        data = {
            'username': 'yenikullanici',
            'first_name': 'Ali',
            'last_name': 'Veli',
            'email': 'ali@example.com',
            'password': 'guclu_sifre_123',
            'password_confirm': 'guclu_sifre_123',
        }
        form = KayitFormu(data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        data = {
            'username': 'yenikullanici',
            'first_name': 'Ali',
            'last_name': 'Veli',
            'email': 'ali@example.com',
            'password': 'sifre123',
            'password_confirm': 'farkli_sifre',
        }
        form = KayitFormu(data)
        self.assertFalse(form.is_valid())

    def test_duplicate_username(self):
        User.objects.create_user('mevcutuser', password='pass1234')
        data = {
            'username': 'mevcutuser',
            'first_name': 'Ali',
            'last_name': 'Veli',
            'email': 'unique@example.com',
            'password': 'sifre123',
            'password_confirm': 'sifre123',
        }
        form = KayitFormu(data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user('user1', email='var@example.com', password='pass1234')
        data = {
            'username': 'newuser',
            'first_name': 'Ali',
            'last_name': 'Veli',
            'email': 'var@example.com',
            'password': 'sifre123',
            'password_confirm': 'sifre123',
        }
        form = KayitFormu(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_save_creates_profil(self):
        data = {
            'username': 'testuser',
            'first_name': 'Ali',
            'last_name': 'Veli',
            'email': 'ali@example.com',
            'password': 'guclu_sifre_123',
            'password_confirm': 'guclu_sifre_123',
            'telefon': '05551234567',
        }
        form = KayitFormu(data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(UyeProfil.objects.filter(kullanici=user).exists())
        self.assertEqual(user.profil.telefon, '05551234567')


class DegerlendirmeFormuTest(TestCase):
    def test_valid(self):
        form = DegerlendirmeFormu(data={'puan': 4, 'yorum': 'Guzel kitap'})
        self.assertTrue(form.is_valid())

    def test_valid_without_yorum(self):
        form = DegerlendirmeFormu(data={'puan': 3, 'yorum': ''})
        self.assertTrue(form.is_valid())

    def test_invalid_puan_zero(self):
        form = DegerlendirmeFormu(data={'puan': 0, 'yorum': ''})
        self.assertFalse(form.is_valid())

    def test_invalid_puan_six(self):
        form = DegerlendirmeFormu(data={'puan': 6, 'yorum': ''})
        self.assertFalse(form.is_valid())

    def test_missing_puan(self):
        form = DegerlendirmeFormu(data={'yorum': 'Yorum var ama puan yok'})
        self.assertFalse(form.is_valid())


class OduncAlmaFormuTest(TestCase):
    def setUp(self):
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Kitap', yazar=self.yazar, yayin_yili=2020,
            sayfa_sayisi=200, stok=3,
        )

    def test_valid(self):
        form = OduncAlmaFormu(data={'kitap_id': self.kitap.pk})
        self.assertTrue(form.is_valid())

    def test_invalid_kitap_id(self):
        form = OduncAlmaFormu(data={'kitap_id': 99999})
        self.assertFalse(form.is_valid())

    def test_stok_yok(self):
        self.kitap.stok = 0
        self.kitap.save()
        form = OduncAlmaFormu(data={'kitap_id': self.kitap.pk})
        self.assertFalse(form.is_valid())


# ──────────────────────────────────────────────
# View Testleri
# ──────────────────────────────────────────────

class KitapListesiViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.yazar = Yazar.objects.create(ad='Orhan Pamuk')
        self.kategori = Kategori.objects.create(ad='Roman')
        self.kitap = Kitap.objects.create(
            baslik='Kar', yazar=self.yazar, kategori=self.kategori,
            yayin_yili=2002, sayfa_sayisi=436, stok=5,
        )

    def test_status_200(self):
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertTemplateUsed(response, 'books/kitap_listesi.html')

    def test_kitap_listeleniyor(self):
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'Kar')

    def test_arama(self):
        response = self.client.get(reverse('books:kitap_listesi') + '?q=Kar')
        self.assertContains(response, 'Kar')

    def test_arama_sonucsuz(self):
        response = self.client.get(reverse('books:kitap_listesi') + '?q=olmayankelime')
        self.assertNotContains(response, 'Kar')

    def test_kategori_filtreleme(self):
        baska_kat = Kategori.objects.create(ad='Siir')
        response = self.client.get(
            reverse('books:kitap_listesi') + f'?kategori={baska_kat.pk}'
        )
        self.assertNotContains(response, 'Kar')


class KitapDetayViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Test Kitap', yazar=self.yazar,
            yayin_yili=2020, sayfa_sayisi=200, stok=5,
        )

    def test_status_200(self):
        response = self.client.get(reverse('books:kitap_detay', args=[self.kitap.pk]))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('books:kitap_detay', args=[self.kitap.pk]))
        self.assertTemplateUsed(response, 'books/kitap_detay.html')

    def test_context_contains_kitap(self):
        response = self.client.get(reverse('books:kitap_detay', args=[self.kitap.pk]))
        self.assertEqual(response.context['kitap'], self.kitap)

    def test_404_for_invalid_pk(self):
        response = self.client.get(reverse('books:kitap_detay', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_degerlendirme_form_for_authenticated_user(self):
        user = User.objects.create_user('u', password='p1234567')
        self.client.login(username='u', password='p1234567')
        response = self.client.get(reverse('books:kitap_detay', args=[self.kitap.pk]))
        self.assertIsNotNone(response.context['degerlendirme_form'])

    def test_no_form_for_anonymous(self):
        response = self.client.get(reverse('books:kitap_detay', args=[self.kitap.pk]))
        self.assertIsNone(response.context['degerlendirme_form'])


class YazarDetayViewTest(TestCase):
    def setUp(self):
        self.yazar = Yazar.objects.create(ad='Yazar A', dogum_yili=1970)

    def test_status_200(self):
        response = self.client.get(reverse('books:yazar_detay', args=[self.yazar.pk]))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('books:yazar_detay', args=[self.yazar.pk]))
        self.assertTemplateUsed(response, 'books/yazar_detay.html')

    def test_404_for_invalid_pk(self):
        response = self.client.get(reverse('books:yazar_detay', args=[99999]))
        self.assertEqual(response.status_code, 404)


class DashboardViewTest(TestCase):
    def test_status_200(self):
        response = self.client.get(reverse('books:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('books:dashboard'))
        self.assertTemplateUsed(response, 'books/dashboard.html')

    def test_context_keys(self):
        response = self.client.get(reverse('books:dashboard'))
        for key in ['toplam_kitap', 'toplam_yazar', 'toplam_uye',
                     'aktif_odunc', 'geciken_odunc', 'populer_kitaplar',
                     'en_yuksek_puanli', 'aktif_uyeler', 'kategori_dagilimi',
                     'aylik_trend', 'son_islemler']:
            self.assertIn(key, response.context)


class KayitViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse('books:kayit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/kayit.html')

    def test_post_valid(self):
        data = {
            'username': 'yeniuser',
            'first_name': 'Ali',
            'last_name': 'Veli',
            'email': 'ali@example.com',
            'password': 'guclusifre123',
            'password_confirm': 'guclusifre123',
        }
        response = self.client.post(reverse('books:kayit'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='yeniuser').exists())

    def test_authenticated_user_redirected(self):
        User.objects.create_user('u', password='p1234567')
        self.client.login(username='u', password='p1234567')
        response = self.client.get(reverse('books:kayit'))
        self.assertEqual(response.status_code, 302)


class GirisViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')

    def test_get(self):
        response = self.client.get(reverse('books:giris'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/giris.html')

    def test_post_valid(self):
        response = self.client.post(reverse('books:giris'), {
            'username': 'testuser',
            'password': 'pass1234',
        })
        self.assertEqual(response.status_code, 302)

    def test_post_invalid(self):
        response = self.client.post(reverse('books:giris'), {
            'username': 'testuser',
            'password': 'yanlis_sifre',
        })
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('books:giris'))
        self.assertEqual(response.status_code, 302)


class CikisViewTest(TestCase):
    def test_cikis(self):
        user = User.objects.create_user('testuser', password='pass1234')
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('books:cikis'))
        self.assertEqual(response.status_code, 302)


class ProfilViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testuser', password='pass1234',
            first_name='Ali', last_name='Veli', email='ali@example.com',
        )
        self.client.login(username='testuser', password='pass1234')

    def test_get(self):
        response = self.client.get(reverse('books:profil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/profil.html')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('books:profil'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('giris', response.url)

    def test_post_update(self):
        response = self.client.post(reverse('books:profil'), {
            'first_name': 'Ahmet',
            'last_name': 'Yilmaz',
            'email': 'ahmet@example.com',
            'telefon': '05551234567',
            'adres': 'Istanbul',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Ahmet')


class OduncAlViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Kitap', yazar=self.yazar, yayin_yili=2020,
            sayfa_sayisi=200, stok=3,
        )
        self.client.login(username='testuser', password='pass1234')

    def test_get(self):
        response = self.client.get(reverse('books:odunc_al', args=[self.kitap.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/odunc_al.html')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('books:odunc_al', args=[self.kitap.pk]))
        self.assertEqual(response.status_code, 302)

    def test_post_odunc_al(self):
        response = self.client.post(
            reverse('books:odunc_al', args=[self.kitap.pk]),
            {'kitap_id': self.kitap.pk},
        )
        self.assertEqual(response.status_code, 302)
        self.kitap.refresh_from_db()
        self.assertEqual(self.kitap.stok, 2)
        self.assertTrue(
            OduncAlma.objects.filter(uye=self.user, kitap=self.kitap, aktif=True).exists()
        )

    def test_stok_yok_odunc_alinamaz(self):
        """Stok 0 olunca form gecersiz kalir, sayfa tekrar render edilir (200)."""
        self.kitap.stok = 0
        self.kitap.save()
        response = self.client.post(
            reverse('books:odunc_al', args=[self.kitap.pk]),
            {'kitap_id': self.kitap.pk},
        )
        # Form validation reddeder, sayfa tekrar gosterilir
        self.assertEqual(response.status_code, 200)
        # Odunc islemi olusturulmamis olmali
        self.assertFalse(
            OduncAlma.objects.filter(uye=self.user, kitap=self.kitap).exists()
        )

    def test_zaten_odunc_alinmis(self):
        OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        response = self.client.post(
            reverse('books:odunc_al', args=[self.kitap.pk]),
            {'kitap_id': self.kitap.pk},
        )
        self.assertEqual(response.status_code, 302)
        # Stok degismemeli
        self.kitap.refresh_from_db()
        self.assertEqual(self.kitap.stok, 3)


class IadeEtViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Kitap', yazar=self.yazar, yayin_yili=2020,
            sayfa_sayisi=200, stok=2,
        )
        self.odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        self.client.login(username='testuser', password='pass1234')

    def test_get(self):
        response = self.client.get(reverse('books:iade_et', args=[self.odunc.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/iade_et.html')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('books:iade_et', args=[self.odunc.pk]))
        self.assertEqual(response.status_code, 302)

    def test_post_iade(self):
        response = self.client.post(reverse('books:iade_et', args=[self.odunc.pk]))
        self.assertEqual(response.status_code, 302)
        self.odunc.refresh_from_db()
        self.assertFalse(self.odunc.aktif)
        self.assertIsNotNone(self.odunc.teslim_tarihi)
        self.kitap.refresh_from_db()
        self.assertEqual(self.kitap.stok, 3)

    def test_baskasinin_odunc_islemini_iade_edemez(self):
        diger_user = User.objects.create_user('diger', password='pass1234')
        self.client.login(username='diger', password='pass1234')
        response = self.client.get(reverse('books:iade_et', args=[self.odunc.pk]))
        self.assertEqual(response.status_code, 404)


class DegerlendirmeEkleViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Kitap', yazar=self.yazar, yayin_yili=2020,
            sayfa_sayisi=200, stok=3,
        )
        self.client.login(username='testuser', password='pass1234')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse('books:degerlendirme_ekle', args=[self.kitap.pk]),
            {'puan': 4, 'yorum': 'Guzel'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('giris', response.url)

    def test_post_degerlendirme_basarili(self):
        response = self.client.post(
            reverse('books:degerlendirme_ekle', args=[self.kitap.pk]),
            {'puan': 5, 'yorum': 'Harika bir kitap'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            KitapDegerlendirme.objects.filter(
                kullanici=self.user, kitap=self.kitap
            ).exists()
        )

    def test_tekrar_degerlendirme_engellenir(self):
        KitapDegerlendirme.objects.create(
            kullanici=self.user, kitap=self.kitap, puan=4,
        )
        response = self.client.post(
            reverse('books:degerlendirme_ekle', args=[self.kitap.pk]),
            {'puan': 2, 'yorum': 'Tekrar'},
        )
        self.assertEqual(response.status_code, 302)
        # Hala sadece 1 degerlendirme olmali
        self.assertEqual(
            KitapDegerlendirme.objects.filter(
                kullanici=self.user, kitap=self.kitap
            ).count(),
            1,
        )

    def test_gecersiz_puan(self):
        response = self.client.post(
            reverse('books:degerlendirme_ekle', args=[self.kitap.pk]),
            {'puan': '', 'yorum': 'Puan yok'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            KitapDegerlendirme.objects.filter(
                kullanici=self.user, kitap=self.kitap
            ).exists()
        )


# ──────────────────────────────────────────────
# Template Icerik Testleri
# ──────────────────────────────────────────────

class TemplateContentTest(TestCase):
    """Template icindeki duzeltilen hatalari dogrulayan testler."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass1234')
        self.yazar = Yazar.objects.create(ad='Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Test Kitap', yazar=self.yazar,
            yayin_yili=2020, sayfa_sayisi=200, stok=7,
        )
        self.client.login(username='testuser', password='pass1234')

    def test_odunc_al_iade_suresi_sabit_15(self):
        """odunc_al.html 15 gun yazmali, stok adedi degil."""
        response = self.client.get(reverse('books:odunc_al', args=[self.kitap.pk]))
        content = response.content.decode()
        # Iade suresi satirinda "15 gun" olmali
        self.assertIn('15 gun', content)
        # Iade notu satirinda "7 gun" OLMAMALI (stok = 7)
        self.assertNotIn('7 gun icinde iade', content)

    def test_iade_et_confirm_return_class(self):
        """iade_et.html'de confirm-return sinifi olmali."""
        odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        response = self.client.get(reverse('books:iade_et', args=[odunc.pk]))
        content = response.content.decode()
        self.assertIn('confirm-return', content)
        self.assertIn('confirm-wrapper', content)

    def test_iade_et_has_confirm_wrapper(self):
        """iade_et.html'de confirm-wrapper div'i olmali."""
        odunc = OduncAlma.objects.create(uye=self.user, kitap=self.kitap)
        response = self.client.get(reverse('books:iade_et', args=[odunc.pk]))
        self.assertContains(response, 'confirm-wrapper')


# ──────────────────────────────────────────────
# Chat Widget Tasarim Testleri
# ──────────────────────────────────────────────

class ChatWidgetDesignTest(TestCase):
    """Chat widget'inin tum sayfalarda gorundugundan emin olan testler."""

    def setUp(self):
        self.client = Client()
        self.yazar = Yazar.objects.create(ad='Test Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Test Kitap', yazar=self.yazar,
            yayin_yili=2020, sayfa_sayisi=200, stok=5,
        )

    def test_chat_toggle_button_on_kitap_listesi(self):
        """Kitap listesi sayfasinda chat toggle butonu olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'id="chatToggleBtn"')
        self.assertContains(response, 'chat-toggle-btn')

    def test_chat_window_on_kitap_listesi(self):
        """Kitap listesi sayfasinda chat penceresi HTML'i olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'id="chatWindow"')
        self.assertContains(response, 'chat-window')

    def test_chat_header_elements(self):
        """Chat header'inda baslik ve durum bilgisi olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'Kutuphane Destek')
        self.assertContains(response, 'chat-header')
        self.assertContains(response, 'status-dot')

    def test_chat_messages_area(self):
        """Chat mesaj alani ve ornek mesajlar olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'chat-body')
        self.assertContains(response, 'chat-message-incoming')
        self.assertContains(response, 'chat-message-outgoing')

    def test_chat_input_area(self):
        """Chat mesaj girdi alani ve gonder butonu olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'id="chatInput"')
        self.assertContains(response, 'id="chatSendBtn"')
        self.assertContains(response, 'chat-footer')

    def test_chat_quick_replies(self):
        """Hizli yanit butonlari olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'chat-quick-reply')
        self.assertContains(response, 'Kitap Ara')
        self.assertContains(response, 'Iade Tarihleri')
        self.assertContains(response, 'Takas Bilgisi')

    def test_chat_widget_on_dashboard(self):
        """Dashboard sayfasinda da chat widget gozukmeli."""
        response = self.client.get(reverse('books:dashboard'))
        self.assertContains(response, 'id="chatToggleBtn"')
        self.assertContains(response, 'id="chatWindow"')

    def test_chat_widget_on_kitap_detay(self):
        """Kitap detay sayfasinda da chat widget gozukmeli."""
        response = self.client.get(
            reverse('books:kitap_detay', args=[self.kitap.pk])
        )
        self.assertContains(response, 'id="chatToggleBtn"')
        self.assertContains(response, 'id="chatWindow"')

    def test_chat_widget_on_giris(self):
        """Giris sayfasinda da chat widget gozukmeli."""
        response = self.client.get(reverse('books:giris'))
        self.assertContains(response, 'id="chatToggleBtn"')
        self.assertContains(response, 'id="chatWindow"')

    def test_chat_css_loaded(self):
        """CSS dosyasi yuklenmeli (style.css icinde chat stilleri var)."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'css/style.css')

    def test_chat_javascript_inline(self):
        """Chat icin JavaScript kodu sayfada olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'chatToggleBtn')
        self.assertContains(response, 'chatWindow')
        self.assertContains(response, 'addEventListener')

    def test_chat_typing_indicator(self):
        """Yazma gostergesi (typing indicator) olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'id="chatTyping"')
        self.assertContains(response, 'chat-typing-dots')

    def test_chat_badge_notification(self):
        """Chat butonunda bildirim badge'i olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'chat-badge')


# ──────────────────────────────────────────────
# Banner Testleri
# ──────────────────────────────────────────────

class HeroBannerTest(TestCase):
    """ALI OZCAN banner'inin tum sayfalarda gorundugundan emin olan testler."""

    def setUp(self):
        self.client = Client()
        self.yazar = Yazar.objects.create(ad='Test Yazar')
        self.kitap = Kitap.objects.create(
            baslik='Test Kitap', yazar=self.yazar,
            yayin_yili=2020, sayfa_sayisi=200, stok=5,
        )

    def test_banner_on_kitap_listesi(self):
        """Kitap listesi sayfasinda banner olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'hero-banner')
        self.assertContains(response, 'ALI OZCAN')

    def test_banner_on_dashboard(self):
        """Dashboard sayfasinda banner olmali."""
        response = self.client.get(reverse('books:dashboard'))
        self.assertContains(response, 'hero-banner')
        self.assertContains(response, 'ALI OZCAN')

    def test_banner_on_kitap_detay(self):
        """Kitap detay sayfasinda banner olmali."""
        response = self.client.get(
            reverse('books:kitap_detay', args=[self.kitap.pk])
        )
        self.assertContains(response, 'hero-banner')
        self.assertContains(response, 'ALI OZCAN')

    def test_banner_on_giris(self):
        """Giris sayfasinda banner olmali."""
        response = self.client.get(reverse('books:giris'))
        self.assertContains(response, 'hero-banner')
        self.assertContains(response, 'ALI OZCAN')

    def test_banner_title_centered(self):
        """Banner h1 etiketi ile hero-banner-title class'i olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        self.assertContains(response, 'hero-banner-title')

    def test_banner_between_nav_and_container(self):
        """Banner, nav ile container arasinda olmali."""
        response = self.client.get(reverse('books:kitap_listesi'))
        content = response.content.decode()
        nav_end = content.index('</nav>')
        banner_pos = content.index('hero-banner')
        container_pos = content.index('class="container"')
        self.assertLess(nav_end, banner_pos)
        self.assertLess(banner_pos, container_pos)
