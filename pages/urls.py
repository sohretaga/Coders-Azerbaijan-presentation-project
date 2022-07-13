from django.urls import path
from . import views
from product import views as productviews, wishlist
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.userRegister, name='register'),
    path('login/', views.userLogin, name='login'),
    path('logout/', views.userLogot, name='logout'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('account/', views.account, name='account'),
    path('account/sell/', productviews.sell, name='sell'),
    path('products/<slug:category_slug>/', productviews.products, name='category_slug'),
    path('products/<slug:category_slug>/<int:id>/', productviews.product_detail, name='product_detail'),
    path('delete/<int:id>/', productviews.delete_product, name='delete_product'),
    path('add_comment/<int:id>/', productviews.addcomment, name='add_comment'),
    path('products/filter/<slug:slug>/', productviews.filter, name='brand'),
    path('products/topfilter/', productviews.topFilter, name='topfilter'),

    path('add-to-cart/', productviews.add_to_cart, name='add_to_cart'),
    path('delete-from-cart/', productviews.delete_cart_item, name='delete_cart_item'),
    path('update-cart/', productviews.update_cart_item, name='update_cart'),
    path('clean-cart', productviews.cleanCart, name = 'cleancart'),

    path('add-to-wishlist/', productviews.add_to_wishlist, name='add_to_wishlist'),
    path('delete-from-wishlist/', productviews.delete_wishlist_item, name='delete_wishlist_item'),

    path('add-to-compare/', productviews.add_to_compare, name="add_to_compare"),
    path('delete-from-compare/', productviews.delete_compare_item, name="delete_compare_item"),
    path('clean-compare/', productviews.cleanCompare, name = 'cleancompare'),

    path('shopcart/', productviews.shopcart, name='shopcart'),
    path('wishlist/', productviews.wishlist, name='wishlist'),
    path('compare/', productviews.compare, name='compare'),
    path('search/', productviews.search, name='search'),
    path('checkout/', productviews.checkout, name='checkout'),
    path('payment/', productviews.payment, name='payment'),

]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)