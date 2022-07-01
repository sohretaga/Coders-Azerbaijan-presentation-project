from datetime import date
from hashlib import blake2b
from statistics import mode
from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.

class CustomUser(User):
    user_phone = models.IntegerField()

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return '>>'.join(full_path[::-1])



class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    main_image = models.ImageField(upload_to='product_images/%Y/%m/%d/')
    detail = models.TextField()
    keywords = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    price = models.FloatField()
    brand = models.CharField(max_length=50, default='Markon', verbose_name='Brand (Default: Markon)')
    sale = models.IntegerField(blank=True, null=True, verbose_name="Sale (%)")
    bestseller = models.BooleanField(default=False)
    amount = models.IntegerField(blank=True, null=True)
    available = models.BooleanField(default=True)
    stock = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def discount(self):
        dis = float(self.price - (self.price * self.sale) / 100)
        ln = ''
        if len(str(dis)) > 3:
            for i in str(dis):
                ln += i
                dis = float(ln)
                if len(ln) > 3:
                    break
        return dis

    def sellerPhone(self):
        for num in CustomUser.objects.filter(id=self.user.id).values_list('user_phone'):
            for num in num:
                return num


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/%Y/%m/%d/')
    date_created = models.DateTimeField(auto_now_add=True)


class ProductComment(models.Model):
    RATING = (
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    good_sides = models.TextField(max_length=200)
    bad_sides = models.TextField(max_length=200)
    comment = models.TextField(max_length=300)
    rating = models.IntegerField(choices=RATING, default=0)
    date_created = models.DateTimeField(auto_now_add=True)


class Checkout(models.Model):
    cardname  = models.CharField(max_length=50, null=False, blank=False)
    cardnumber = models.IntegerField(null=False, blank=False)
    expmonth = models.IntegerField()
    expyear = models.IntegerField(null=False, blank=False)
    cvv = models.IntegerField(null=False, blank=False)
    fullname = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True)
    address = models.TextField(max_length=150, null=False, blank=False)
    city = models.CharField(max_length=30, null=False, blank=False)
    state = models.CharField(max_length=30, null=False, blank=False)
    zip = models.IntegerField()
    coupon = models.CharField(max_length=6, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True)

    def main_name(self) -> str:
        return self.fullname + " / " + str(self.date)

    def __str__(self) -> str:
        return str(self.id)
    
class Sold(models.Model):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE)
    product = models.IntegerField()

    def name(self) -> str:
        return self.checkout.fullname


class Cupone(models.Model):
    pass