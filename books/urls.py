from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.kitap_listesi, name='kitap_listesi'),
    path('kitap/<int:pk>/', views.kitap_detay, name='kitap_detay'),
    path('yazar/<int:pk>/', views.yazar_detay, name='yazar_detay'),
]
