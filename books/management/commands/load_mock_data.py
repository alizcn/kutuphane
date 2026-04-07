from django.core.management.base import BaseCommand
from books.models import Yazar, Kategori, Kitap


class Command(BaseCommand):
    help = 'Mock verileri yükler'

    def handle(self, *args, **options):
        if Kitap.objects.exists():
            self.stdout.write('Veriler zaten mevcut, atlanıyor.')
            return

        # Kategoriler
        roman = Kategori.objects.create(ad='Roman')
        siir = Kategori.objects.create(ad='Şiir')
        tarih = Kategori.objects.create(ad='Tarih')
        bilim = Kategori.objects.create(ad='Bilim Kurgu')
        felsefe = Kategori.objects.create(ad='Felsefe')

        # Yazarlar
        orhan_pamuk = Yazar.objects.create(
            ad='Orhan Pamuk', dogum_yili=1952,
            biyografi='Nobel ödüllü Türk romancı. İstanbul doğumlu.',
        )
        sabahattin_ali = Yazar.objects.create(
            ad='Sabahattin Ali', dogum_yili=1907,
            biyografi='Türk edebiyatının en önemli hikaye ve roman yazarlarından biri.',
        )
        nazim_hikmet = Yazar.objects.create(
            ad='Nazım Hikmet', dogum_yili=1902,
            biyografi='Türk şiirinin en büyük isimlerinden biri.',
        )
        oguz_atay = Yazar.objects.create(
            ad='Oğuz Atay', dogum_yili=1934,
            biyografi='Türk edebiyatında postmodern akımın öncüsü.',
        )
        isaac_asimov = Yazar.objects.create(
            ad='Isaac Asimov', dogum_yili=1920,
            biyografi='Bilim kurgu edebiyatının en önemli yazarlarından biri.',
        )
        albert_camus = Yazar.objects.create(
            ad='Albert Camus', dogum_yili=1913,
            biyografi='Nobel ödüllü Fransız-Cezayirli yazar ve filozof.',
        )

        # Kitaplar
        kitaplar = [
            {'baslik': 'Benim Adım Kırmızı', 'yazar': orhan_pamuk, 'kategori': roman, 'yayin_yili': 1998, 'sayfa_sayisi': 472, 'stok': 12, 'aciklama': '16. yüzyıl Osmanlı İstanbul\'unda minyatür sanatçıları arasında geçen bir cinayet hikayesi.'},
            {'baslik': 'Masumiyet Müzesi', 'yazar': orhan_pamuk, 'kategori': roman, 'yayin_yili': 2008, 'sayfa_sayisi': 592, 'stok': 8, 'aciklama': '1975 İstanbul\'unda başlayan tutkulu bir aşk hikayesi.'},
            {'baslik': 'Kürk Mantolu Madonna', 'yazar': sabahattin_ali, 'kategori': roman, 'yayin_yili': 1943, 'sayfa_sayisi': 160, 'stok': 25, 'aciklama': 'Berlin\'de geçen unutulmaz bir aşk romanı.'},
            {'baslik': 'İçimizdeki Şeytan', 'yazar': sabahattin_ali, 'kategori': roman, 'yayin_yili': 1940, 'sayfa_sayisi': 224, 'stok': 15, 'aciklama': 'Toplumsal baskılar altında ezilen bireyin iç dünyasını anlatan roman.'},
            {'baslik': 'Memleketimden İnsan Manzaraları', 'yazar': nazim_hikmet, 'kategori': siir, 'yayin_yili': 1966, 'sayfa_sayisi': 680, 'stok': 6, 'aciklama': 'Türkiye\'nin toplumsal panoramasını çizen destansı şiir.'},
            {'baslik': 'Tutunamayanlar', 'yazar': oguz_atay, 'kategori': roman, 'yayin_yili': 1972, 'sayfa_sayisi': 724, 'stok': 10, 'aciklama': 'Türk edebiyatının en önemli postmodern romanlarından biri.'},
            {'baslik': 'Vakıf', 'yazar': isaac_asimov, 'kategori': bilim, 'yayin_yili': 1951, 'sayfa_sayisi': 244, 'stok': 18, 'aciklama': 'Galaktik İmparatorluk\'un çöküşünü ve yeniden doğuşunu anlatan bilim kurgu klasiği.'},
            {'baslik': 'Ben, Robot', 'yazar': isaac_asimov, 'kategori': bilim, 'yayin_yili': 1950, 'sayfa_sayisi': 253, 'stok': 14, 'aciklama': 'Robotik üç yasasını tanıtan öykü derlemesi.'},
            {'baslik': 'Yabancı', 'yazar': albert_camus, 'kategori': felsefe, 'yayin_yili': 1942, 'sayfa_sayisi': 123, 'stok': 20, 'aciklama': 'Absürd felsefesinin en önemli eserlerinden biri.'},
            {'baslik': 'Veba', 'yazar': albert_camus, 'kategori': roman, 'yayin_yili': 1947, 'sayfa_sayisi': 308, 'stok': 9, 'aciklama': 'Cezayir\'in Oran şehrinde salgın hastalıkla mücadeleyi anlatan roman.'},
            {'baslik': 'Kar', 'yazar': orhan_pamuk, 'kategori': roman, 'yayin_yili': 2002, 'sayfa_sayisi': 436, 'stok': 7, 'aciklama': 'Kars şehrinde geçen siyasi gerilim romanı.'},
            {'baslik': 'Tehlikeli Oyunlar', 'yazar': oguz_atay, 'kategori': roman, 'yayin_yili': 1973, 'sayfa_sayisi': 467, 'stok': 5, 'aciklama': 'Tutunamayanlar\'ın devamı niteliğinde postmodern roman.'},
        ]

        for k in kitaplar:
            Kitap.objects.create(**k)

        self.stdout.write(self.style.SUCCESS(
            f'{Yazar.objects.count()} yazar, {Kategori.objects.count()} kategori, {Kitap.objects.count()} kitap oluşturuldu.'
        ))
