# Generated migration for KitapTakasi model and takasa_acik field

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_kitapdegerlendirme'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='kitap',
            name='takasa_acik',
            field=models.BooleanField(default=False, help_text='Bu kitap takasa acik midir?'),
        ),
        migrations.CreateModel(
            name='KitapTakasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('durum', models.CharField(choices=[('beklemede', 'Beklemede'), ('kabul_edildi', 'Kabul Edildi'), ('reddedildi', 'Reddedildi'), ('tamamlandi', 'Tamamlandı')], default='beklemede', max_length=20)),
                ('aciklama', models.TextField(blank=True, help_text='Takas teklifine ait açıklama veya not')),
                ('olusturma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('gunceleme_tarihi', models.DateTimeField(auto_now=True)),
                ('alici', models.ForeignKey(help_text='Takas teklifini alan kullanıcı', on_delete=django.db.models.deletion.CASCADE, related_name='alinan_takas_teklifleri', to=settings.AUTH_USER_MODEL)),
                ('alici_kitap', models.ForeignKey(help_text='Alıcı tarafından verilen kitap', on_delete=django.db.models.deletion.CASCADE, related_name='takas_teklifleri_alici', to='books.kitap')),
                ('gonderici', models.ForeignKey(help_text='Takas teklifini gönderen kullanıcı', on_delete=django.db.models.deletion.CASCADE, related_name='gonderilen_takas_teklifleri', to=settings.AUTH_USER_MODEL)),
                ('gonderici_kitap', models.ForeignKey(help_text='Gönderici tarafından verilen kitap', on_delete=django.db.models.deletion.CASCADE, related_name='takas_teklifleri_gonderici', to='books.kitap')),
            ],
            options={
                'verbose_name': 'Kitap Takası',
                'verbose_name_plural': 'Kitap Takasları',
                'ordering': ['-olusturma_tarihi'],
            },
        ),
    ]
