from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Ana sayfalar
    path('', views.kitap_listesi, name='kitap_listesi'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Kitap & Yazar detay
    path('kitap/<int:pk>/', views.kitap_detay, name='kitap_detay'),
    path('yazar/<int:pk>/', views.yazar_detay, name='yazar_detay'),

    # Kimlik dogrulama
    path('kayit/', views.kayit_view, name='kayit'),
    path('giris/', views.giris_view, name='giris'),
    path('cikis/', views.cikis_view, name='cikis'),
    path('profil/', views.profil_view, name='profil'),

    # Odunc alma / iade
    path('kitap/<int:pk>/odunc-al/', views.odunc_al, name='odunc_al'),
    path('odunc/<int:pk>/iade/', views.iade_et, name='iade_et'),
]
