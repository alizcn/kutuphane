from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UyeProfil


class KayitFormu(forms.ModelForm):
    username = forms.CharField(
        label='Kullanıcı Adı',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Kullanıcı adınız'}),
    )
    first_name = forms.CharField(
        label='Ad',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Adınız'}),
    )
    last_name = forms.CharField(
        label='Soyad',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Soyadınız'}),
    )
    email = forms.EmailField(
        label='E-posta',
        widget=forms.EmailInput(attrs={'placeholder': 'E-posta adresiniz'}),
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'placeholder': 'Şifreniz'}),
    )
    password_confirm = forms.CharField(
        label='Şifre Tekrar',
        widget=forms.PasswordInput(attrs={'placeholder': 'Şifrenizi tekrar girin'}),
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
            raise forms.ValidationError('Bu kullanıcı adı zaten kullanılıyor.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Şifreler eşleşmiyor.')
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
        label='Kullanıcı Adı',
        widget=forms.TextInput(attrs={'placeholder': 'Kullanıcı adınız'}),
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'placeholder': 'Şifreniz'}),
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
