from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UyeProfil, Kitap, KitapDegerlendirme, KullaniciKitap


class KayitFormu(forms.ModelForm):
    username = forms.CharField(
        label='Kullanici Adi',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Kullanici adiniz'}),
    )
    first_name = forms.CharField(
        label='Ad',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Adiniz'}),
    )
    last_name = forms.CharField(
        label='Soyad',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Soyadiniz'}),
    )
    email = forms.EmailField(
        label='E-posta',
        widget=forms.EmailInput(attrs={'placeholder': 'E-posta adresiniz'}),
    )
    password = forms.CharField(
        label='Sifre',
        widget=forms.PasswordInput(attrs={'placeholder': 'Sifreniz'}),
    )
    password_confirm = forms.CharField(
        label='Sifre Tekrar',
        widget=forms.PasswordInput(attrs={'placeholder': 'Sifrenizi tekrar girin'}),
    )
    telefon = forms.CharField(
        label='Telefon',
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '05XX XXX XX XX'}),
    )
    adres = forms.CharField(
        label='Adres',
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Adresiniz', 'rows': 3}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu kullanici adi zaten kullaniliyor.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kullaniliyor.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Sifreler eslesmiyor.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UyeProfil.objects.create(
                kullanici=user,
                telefon=self.cleaned_data.get('telefon', ''),
                adres=self.cleaned_data.get('adres', ''),
            )
        return user


class GirisFormu(AuthenticationForm):
    username = forms.CharField(
        label='Kullanici Adi',
        widget=forms.TextInput(attrs={'placeholder': 'Kullanici adiniz'}),
    )
    password = forms.CharField(
        label='Sifre',
        widget=forms.PasswordInput(attrs={'placeholder': 'Sifreniz'}),
    )


class ProfilFormu(forms.ModelForm):
    first_name = forms.CharField(label='Ad', max_length=150)
    last_name = forms.CharField(label='Soyad', max_length=150)
    email = forms.EmailField(label='E-posta')

    class Meta:
        model = UyeProfil
        fields = ['telefon', 'adres']
        labels = {
            'telefon': 'Telefon',
            'adres': 'Adres',
        }
        widgets = {
            'adres': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.kullanici
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = self.instance.kullanici
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise forms.ValidationError('Bu e-posta adresi baska bir kullanici tarafindan kullaniliyor.')
        return email

    def save(self, commit=True):
        profil = super().save(commit=False)
        user = profil.kullanici
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profil.save()
        return profil


class OduncAlmaFormu(forms.Form):
    """Odunc alma islemini onaylamak icin kullanilan basit form."""
    kitap_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_kitap_id(self):
        kitap_id = self.cleaned_data.get('kitap_id')
        try:
            kitap = Kitap.objects.get(pk=kitap_id)
        except Kitap.DoesNotExist:
            raise forms.ValidationError('Kitap bulunamadi.')
        if kitap.stok <= 0:
            raise forms.ValidationError('Bu kitap su anda stokta bulunmuyor.')
        return kitap_id


class DegerlendirmeFormu(forms.ModelForm):
    """Kitap degerlendirme ve yorum formu."""

    class Meta:
        model = KitapDegerlendirme
        fields = ['puan', 'yorum']
        labels = {
            'puan': 'Puaniniz',
            'yorum': 'Yorumunuz (Opsiyonel)',
        }
        widgets = {
            'yorum': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Kitap hakkindaki dusuncelerinizi paylasabilirsiniz...',
            }),
        }

    def clean_puan(self):
        puan = self.cleaned_data.get('puan')
        if puan is None or not (1 <= int(puan) <= 5):
            raise forms.ValidationError('Puan 1 ile 5 arasinda olmalidir.')
        return puan


# ──────────────────────────────────────────────
# Takas Formları
# ──────────────────────────────────────────────

class KullaniciKitapFormu(forms.ModelForm):
    """Kullanıcının takasa açmak istediği kitabı eklemek için form."""

    class Meta:
        model = KullaniciKitap
        fields = ['kitap_adi', 'yazar_adi', 'aciklama']
        labels = {
            'kitap_adi': 'Kitap Adı',
            'yazar_adi': 'Yazar Adı',
            'aciklama': 'Açıklama / Durum Notu (Opsiyonel)',
        }
        widgets = {
            'kitap_adi': forms.TextInput(attrs={
                'placeholder': 'Kitabın tam adını girin...',
            }),
            'yazar_adi': forms.TextInput(attrs={
                'placeholder': 'Yazarın adını girin...',
            }),
            'aciklama': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Kitabın durumu, baskı bilgisi vb. (opsiyonel)',
            }),
        }


class TakasTeklifiFormu(forms.Form):
    """Takas teklifi gönderme formu."""

    teklif_edilen_kitap = forms.ModelChoiceField(
        queryset=KullaniciKitap.objects.none(),
        label='Teklif Ettiğiniz Kitap',
        empty_label='— Bir kitap seçin —',
        widget=forms.Select(),
    )
    mesaj = forms.CharField(
        label='Mesajınız (Opsiyonel)',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Takas hakkında bir not ekleyebilirsiniz...',
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['teklif_edilen_kitap'].queryset = KullaniciKitap.objects.filter(
                sahip=user, durum='musait'
            )
