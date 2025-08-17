from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import admin
from django import forms
import json

from .models import Platform, Category, Package, Order, Contact, PaymentInfo, Visitor


# Tarih aralığı formu
class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False)


# Custom Admin Site
class CustomAdminSite(AdminSite):
    site_header = _("My Custom Admin")
    site_title = _("My Admin Portal")
    index_title = _("Dashboard")

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.custom_dashboard), name='custom-dashboard'),
        ]
        return custom_urls + urls

    def custom_dashboard(self, request):
        today = now().date()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Dinamik Veriler
        visitors = Visitor.objects.count()
        subscribers = Package.objects.count()

        # Satış ve kar
        if start_date and end_date:
            orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        else:
            orders = Order.objects.filter(created_at__date=today)

        sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        profits = sum([float(order.total_price) - float(order.package.orprice) for order in orders])
        daily_sales = Order.objects.filter(created_at__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0

        # 7 Günlük Satış Grafiği
        labels, sales_data = [], []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime('%d %b'))
            day_sales = Order.objects.filter(created_at__date=day).aggregate(Sum('total_price'))['total_price__sum'] or 0
            sales_data.append(float(day_sales))  # Decimal -> float

        # Ziyaretçi Grafiği
        user_distribution_labels = ['Türkiye', 'ABD', 'Almanya', 'Fransa', 'Diğer']
        user_distribution_data = [
            float(Visitor.objects.filter(country='Türkiye').count()),
            float(Visitor.objects.filter(country='ABD').count()),
            float(Visitor.objects.filter(country='Almanya').count()),
            float(Visitor.objects.filter(country='Fransa').count()),
            float(Visitor.objects.exclude(country__in=['Türkiye','ABD','Almanya','Fransa']).count())
        ]

        # Örnek: Ziyaretçi tablosu için
        indonesia_users = Visitor.objects.filter(country='Indonesia').count()

        context = dict(
            self.each_context(request),
            visitors=visitors,
            subscribers=subscribers,
            sales=float(sales),
            profits=float(profits),
            daily_sales=float(daily_sales),
            sales_chart_labels=json.dumps(labels),
            sales_chart_data=json.dumps(sales_data),
            user_distribution_labels=json.dumps(user_distribution_labels),
            user_distribution_data=json.dumps(user_distribution_data),
            indonesia_users=indonesia_users,
            start_date=start_date,
            end_date=end_date,
        )

        return render(request, 'admin/dashboard.html', context)

# Platform için özelleştirilmiş admin
class PlatformAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'icon', 'slug')  # listede görünmesini istediğin alanlar
    search_fields = ('name',)                    # filtreleme seçenekleri

class OrderAdmin(admin.ModelAdmin):
    list_display = ('package','full_name', 'profile_link','total_price', 'payment_method', 'status')
    search_fields = ('package','full_name')
    list_filter = ('created_at','status')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('platform','name', 'icon','slug',)
    search_fields = ('platform','name')

class PackageAdmin(admin.ModelAdmin):
    list_display = ('category','name', 'quantity',)
    search_fields = ('category','name')

class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = ('full_name','bank_name', 'iban',)
    search_fields = ('full_name','bank_name')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name','email', 'phone','subject')
    search_fields = ('full_name','email')

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address','country', 'visit_date',)
    search_fields = ('country','ip_address')
# Admin Site ve Model Kayıtları
admin_site = CustomAdminSite(name='custom_admin')
admin_site.register(Platform, PlatformAdmin)
admin_site.register(Category,CategoryAdmin)
admin_site.register(Package,PackageAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(Contact,ContactAdmin)
admin_site.register(PaymentInfo,PaymentInfoAdmin)
admin_site.register(Visitor,VisitorAdmin)
