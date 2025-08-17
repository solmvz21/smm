from django.http import JsonResponse
import requests
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Platform, Category,  Package, Order, Contact, PaymentInfo
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import hmac, base64, random
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from django.utils.timezone import now
from .models import Visitor, Order
# views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from django.utils.timezone import now
from .models import Package, Order, Visitor


# Create your views here.

# Ödeme formunu göster (isteğe bağlı)
def order_form_view(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    return render(request, "order_form.html", {"package": package})

def generate_shopier_form(order):
    random_nr = str(random.randint(1000000, 9999999))
    api_key = settings.SHOPIER_API_KEY
    api_secret = settings.SHOPIER_API_SECRET

    args = {
        "API_key": api_key,
        "website_index": 1,
        "platform_order_id": order.id,
        "product_name": order.package.name,
        "product_type": 1,
        "buyer_name": order.full_name.split()[0],
        "buyer_surname": " ".join(order.full_name.split()[1:]),
        "buyer_email": order.email,
        "buyer_account_age": 1,
        "buyer_id_nr": 0,
        "buyer_phone": order.phone,
        "billing_address": "",
        "billing_city": "Unknown",
        "billing_country": "TR",
        "billing_postcode": "",
        "shipping_address": "",
        "shipping_city": "Unknown",
        "shipping_country": "TR",
        "shipping_postcode": "",
        "total_order_value": float(order.total_price),
        "currency": 0,
        "platform": 0,
        "is_in_frame": 1,
        "current_language": 0,
        "modul_version": "1.0.4",
        "random_nr": random_nr
    }

    sign_data = f"{random_nr}{args['platform_order_id']}{args['total_order_value']}{args['currency']}"
    signature = base64.b64encode(
        hmac.new(api_secret.encode(), sign_data.encode(), digestmod='sha256').digest()
    ).decode()
    args['signature'] = signature

    input_fields = "".join([f"<input type='hidden' name='{k}' value='{v}'/>" for k, v in args.items()])

    return f"""
    <html><head><meta charset='UTF-8'></head>
    <body>
    <form action='https://www.shopier.com/ShowProduct/api_pay4.php' method='post' id='shopier_form'>
    {input_fields}
    </form>
    <script>document.getElementById('shopier_form').submit();</script>
    </body></html>
    """

def shopier_payment_post(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = generate_shopier_form(order)
    return HttpResponse(html)

@csrf_exempt
def kategori_getir(request):
    platform_id = request.POST.get("platform_id")
    kategoriler = Category.objects.filter(platform_id=platform_id)
    data = [{'id': k.id, 'ad': k.name} for k in kategoriler]
    return JsonResponse({'kategoriler': data})

@csrf_exempt
def paket_getir(request):
    kategori_id = request.POST.get("kategori_id")
    paketler = Package.objects.filter(category_id=kategori_id)
    data = [{'id': p.id, 'ad': f"{p.quantity}", 'fiyat': float(p.price)} for p in paketler]
    return JsonResponse({'paketler': data})


def index(request):
    platform = Platform.objects.all()
    paketler = Package.objects.filter(is_best_seller=True)
    context = {
        'paketler':paketler,
        'platform':platform,
    }
    return render(request, 'index.html', context)

def hizmet_detay(request, slug):
    platform = get_object_or_404(Platform, slug=slug)
    category = Category.objects.filter(platform=platform)
    context = {
        'platform':platform,
        'category':category,
    }
    return render(request, 'hizmet_detay.html', context)


def paket_detay(request, slug):
    category = get_object_or_404(Category, slug=slug)
    paket = Package.objects.filter(category=category)
    context = {
        'category':category,
        'paket':paket,
        'platform':category.platform,
    }
    return render(request, 'paket_detay.html', context)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def siparis(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    
    if request.method == "POST":
        profile_link = request.POST.get("sp_musteri_link")
        full_name = request.POST.get("sp_musteri_adi")
        phone = request.POST.get("sp_musteri_telefon")
        email = request.POST.get("sp_musteri_mail")
        type = request.POST.get("sp_tur")
        coupon_code = request.POST.get("kupon_kodu")
        payment_method = request.POST.get("odeme_turu")

        price = float(package.price)
        total_price = round(price)

        order = Order.objects.create(
            package=package,
            profile_link=profile_link,
            full_name=full_name,
            phone=phone,
            email=email,
            type=type,
            coupon_code=coupon_code,
            payment_method=payment_method,
            total_price=total_price
        )

        # Eğer ödeme Shopier üzerinden olacaksa direkt formu dön
        if payment_method.lower() == "shopier":
            html = generate_shopier_form(order)
            return HttpResponse(html)

        # Diğer ödeme yöntemleri için normal yönlendirme
        return redirect("siparis_basarili", order_id=order.id)

    price = float(package.price)
    return render(request, 'siparis.html', {
        'package': package,
        'price': price,
    })

# Shopier callback (ödeme durumunu al)
@csrf_exempt
def shopier_callback(request):
    if request.method == "POST":
        try:
            platform_order_id = request.POST.get("platform_order_id")
            status = request.POST.get("status")  # 1: başarılı, 0: başarısız
            signature = request.POST.get("signature")

            random_nr = request.POST.get("random_nr")
            total_order_value = request.POST.get("total_order_value")
            currency = request.POST.get("currency")

            sign_data = f"{random_nr}{platform_order_id}{total_order_value}{currency}"
            expected_signature = base64.b64encode(
                hmac.new(settings.SHOPIER_API_SECRET.encode(), sign_data.encode(), digestmod='sha256').digest()
            ).decode()

            if signature != expected_signature:
                return HttpResponse("Geçersiz imza", status=400)

            # Order'ı güncelle
            from .models import Order
            order = Order.objects.get(id=platform_order_id)
            if status == "1":
                order.status = "completed"
            else:
                order.status = "cancelled"
            order.save()

            return HttpResponse("OK")

        except Order.DoesNotExist:
            return HttpResponse("Sipariş bulunamadı", status=404)
        except Exception as e:
            return HttpResponse(f"Hata: {str(e)}", status=500)

    return HttpResponse("Sadece POST destekleniyor", status=405)


def siparis_basarili(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment_info = PaymentInfo.objects.first()
    return render(request, 'siparis_basarili.html', {'order': order, 'payment_info':payment_info})


def siparis_sorgula(request):
    siparis_no = request.GET.get("siparis_no")

    if not siparis_no:
        return JsonResponse({"status": "error", "message": "Sipariş numarası eksik"}, status=400)

    try:
        order = Order.objects.get(id=siparis_no)  # veya order_number, numara vs. doğru alan neyse
        return JsonResponse({
            "status": "found",
            "siparis_no": order.id,
            "durum": order.status if hasattr(order, 'status') else 'Belirtilmedi',
            "tarih": order.created_at.strftime("%d.%m.%Y %H:%M") if hasattr(order, 'created_at') else 'Yok',
            "urun": order.package.name if hasattr(order, 'package') else 'Paket bilgisi yok'
        })
    except Order.DoesNotExist:
        return JsonResponse({"status": "not_found"})


def send_payment_notification(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    message = (
        f"💰 Yeni Ödeme Bildirimi\n\n"
        f"👤 Ad: {order.full_name}\n"
        f"📞 Telefon: {order.phone}\n"
        f"📧 E-Posta: {order.email}\n"
        f"🔗 Profil: {order.profile_link}\n"
        f"🌐 Platform: {order.package}\n"
        f"📦 Paket: {order.package.category.name} - {order.package.quantity}\n"
        f"💵 Tutar: {order.total_price} TL\n"
        f"🕒 Tarih: {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )

    telegram_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    requests.post(telegram_url, data=payload)

    # Bildirim gönderildikten sonra başarılı sayfaya yönlendir
    return render(request, 'payment_notification_success.html')


def hizmet(request):
    return render(request,'hizmet.html')

def iade(request):
    return render(request,'iade.html')

def blog(request):
    return render(request,'blog.html')

def iletisim(request):
    if request.method == "POST":
        full_name = request.POST.get("i_ad_soyad")
        email = request.POST.get("i_mail")
        phone = request.POST.get("i_telefon")
        subject = request.POST.get("i_konu")
        message_text = request.POST.get("i_mesaj")

        # Veriyi kaydet
        contact = Contact.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )

        # Telegram bildirimi gönder
        telegram_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        message = (
            f"📩 Yeni İletişim Mesajı\n\n"
            f"👤 İsim: {full_name}\n"
            f"📧 E-posta: {email}\n"
            f"📞 Telefon: {phone or 'Belirtilmemiş'}\n"
            f"📝 Konu: {subject}\n"
            f"💬 Mesaj: {message_text}\n"
            f"🕒 Tarih: {contact.created_at.strftime('%d.%m.%Y %H:%M')}"
        )

        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(telegram_url, data=payload)

        return redirect('index')  # veya kendi iletişim sayfanızın url adı

    # GET isteği için formu göster
    return render(request, 'iletisim.html')