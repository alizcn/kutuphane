import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_kitapdegerlendirme'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KullaniciKitap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kitap_adi', models.CharField(max_length=200, verbose_name='Kitap Adı')),
                ('yazar_adi', models.CharField(max_length=100, verbose_name='Yazar Adı')),
                ('aciklama', models.TextField(blank=True, verbose_name='Açıklama / Durum Notu')),
                ('durum', models.CharField(
                    choices=[
                        ('musait', 'Müsait'),
                        ('takasta', 'Takasta'),
                        ('kaldirildi', 'Kaldırıldı'),
                    ],
                    default='musait',
                    max_length=20,
                    verbose_name='Durum',
                )),
                ('olusturma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('sahip', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='kullanici_kitaplari',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Kullanıcı Kitabı',
                'verbose_name_plural': 'Kullanıcı Kitapları',
                'ordering': ['-olusturma_tarihi'],
            },
        ),
        migrations.CreateModel(
            name='TakasTeklifi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mesaj', models.TextField(blank=True, verbose_name='Mesaj')),
                ('durum', models.CharField(
                    choices=[
                        ('beklemede', 'Beklemede'),
                        ('onaylandi', 'Onaylandı'),
                        ('reddedildi', 'Reddedildi'),
                        ('iptal', 'İptal Edildi'),
                    ],
                    default='beklemede',
                    max_length=20,
                    verbose_name='Durum',
                )),
                ('olusturma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('guncelleme_tarihi', models.DateTimeField(auto_now=True)),
                ('alici', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='alinan_teklifler',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('gonderen', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='gonderilen_teklifler',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('istenen_kitap', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='gelen_teklifler',
                    to='books.kullanicikitap',
                )),
                ('teklif_edilen_kitap', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='verilen_teklifler',
                    to='books.kullanicikitap',
                )),
            ],
            options={
                'verbose_name': 'Takas Teklifi',
                'verbose_name_plural': 'Takas Teklifleri',
                'ordering': ['-olusturma_tarihi'],
            },
        ),
    ]
