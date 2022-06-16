from django.contrib import admin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import Category, Product, ProductImages, ProductComment, Checkout, Sold
# Register your models here.


class ImageInline(admin.TabularInline):
    model = ProductImages
    extra = 3


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'available', 'date_created')
    inlines = [ImageInline]


admin.site.register(ProductImages)
admin.site.register(Product, ProductAdmin)
admin.site.register(

    Category,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
    prepopulated_fields={'slug': ('name',)}

)

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'product','date_created')
    list_display_links = ('user', 'product')

class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('main_name','email', 'city', 'zip')

class SoldAdmin(admin.ModelAdmin):
    list_display = ('name', 'checkout', 'product')

admin.site.register(ProductComment, CommentsAdmin)
admin.site.register(Checkout, CheckoutAdmin)
admin.site.register(Sold, SoldAdmin)