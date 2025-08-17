from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('kategori_getir/', views.kategori_getir, name='kategori_getir'),
    path('paket_getir/', views.paket_getir, name='paket_getir'),
    path('hizmet-sartlari', views.hizmet, name='hizmet'),
    path('iade-kosullari', views.iade, name='iade'),
    path('siparis/<int:package_id>/', views.siparis, name='siparis'),
    path('siparis-basarili/<int:order_id>/', views.siparis_basarili, name='siparis_basarili'),
    path("siparis-sorgula/", views.siparis_sorgula, name="siparis_sorgula"),
    path('odeme-bildirimi/<int:order_id>/', views.send_payment_notification, name='send_payment_notification'),
    path('blog', views.blog, name='blog'),
    path('iletisim', views.iletisim, name='iletisim'),
    path('platform/<slug:slug>', views.hizmet_detay, name='hizmet_detay'),
    path('paket/<slug:slug>', views.paket_detay, name='paket_detay'),
    path('shopier/order/<int:package_id>/', views.order_form_view, name='shopier_order_form'),
    path('shopier/payment/<int:order_id>/', views.shopier_payment_post, name='shopier_payment'),
    path('shopier/callback/', views.shopier_callback, name='shopier_callback'),
]