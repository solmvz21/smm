from django.db import models
from django.utils.text import slugify
from django.db.models import Sum
from datetime import timedelta
from django.utils.timezone import now

# Create your models here.


class Platform(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=200)
    desc = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Category(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=200)
    desc = models.TextField()
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Package(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    orprice = models.DecimalField(max_digits=9, decimal_places=2)
    is_best_seller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    quantity = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)
    text1 = models.CharField(max_length=200)
    text2 = models.CharField(max_length=200)
    text3 = models.CharField(max_length=200)
    text4 = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Order(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('bireysel', 'Bireysel'),
        ('kurumsal', 'Kurumsal'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    profile_link = models.URLField()
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.package}"



class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
    
class PaymentInfo(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="İsim Soyisim")
    bank_name = models.CharField(max_length=255, verbose_name="Banka")
    iban = models.CharField(max_length=34, verbose_name="IBAN")

    def __str__(self):
        return f"{self.full_name} - {self.bank_name}"


class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, blank=True, null=True)
    visit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visitor from {self.country} on {self.visit_date.strftime('%d.%m.%Y %H:%M')}"

