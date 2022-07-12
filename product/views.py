from os import stat
from sre_constants import SUCCESS
from unicodedata import category
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.template.loader import render_to_string

from product.models import Category, Product, ProductImages, ProductComment, Checkout, Sold, Brand
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.

def products(request, category_slug):
    category = Category.objects.all()
    products = Product.objects.all().filter(category__slug=category_slug)
    best_products = Product.objects.all().filter(bestseller=True)
    sale = Product.objects.all().filter(sale__gte=0)
    used_products = Product.objects.all().filter(used=True)
    all_products = Product.objects.all()
    sidebar = Product.objects.all().order_by('?')[:4]
    brands = Brand.objects.all()
    context = {'category': category,
               'products': products,
               'best_products': best_products,
               'sale': sale,
               'used_products': used_products,
               'all_products': all_products,
               'sidebar': sidebar,
               'brands': brands,
               }
    return render(request, 'products.html', context)


def product_detail(request, category_slug, id):

    # Check product rating
    ratings = ProductComment.objects.filter(product_id=id).values_list('rating')
    li = list()
    product_rating = 0
    for r in ratings:
        for i in r:
            li.append(i)
    total = 0
    if len(li) > 0:
        for rating in li:
            total = rating+total
        product_rating = total/len(li)
        if product_rating > int(product_rating):
            product_rating += 1
    product_rating = int(product_rating)


    category = Category.objects.all()
    users = User.objects.all()
    product = get_object_or_404(Product, category__slug = category_slug, id=id)
    images = ProductImages.objects.filter(product_id=id)
    similar = Product.objects.all().exclude(category__slug=category_slug, id=id).filter(category__slug=category_slug,).order_by('?')[:8]
    comments = ProductComment.objects.all().filter(product_id=id).order_by('-date_created')
    comments_count = ProductComment.objects.all().filter(product_id=id).count()
    context = {
        'category': category,
        'product': product,
        'images': images,
        'similar': similar,
        'users': users,
        'comments': comments,
        'count': comments_count,
        'product_rating': product_rating,

    }

    return render(request, 'detail.html', context)

@login_required(login_url='/login/')
def sell(request):
    category = Category.objects.all()
    context = {'category': category}
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        up_category = request.POST.get('up_category')
        keywords = request.POST.get('keywords')
        description = request.POST.get('description')
        main_image = request.FILES.get('main_image')
        price = request.POST.get('price')
        detail = request.POST.get('detail')
        if product_name == '' or up_category == 'Kateqoriya seç' or keywords == '' or description == '' or price == '' or detail == '':
            messages.warning(request, 'Bütün xanaları doldurduğunuzdan əmin olun!')
        else:
            cat = Category.objects.get(pk=up_category)
            newUserProduct = Product(    user=request.user,
                                         used=True,
                                         brand=request.user,
                                         name=product_name,
                                         category=cat,
                                         keywords=keywords,
                                         description=description,
                                         price=price,
                                         detail=detail,
                                         main_image=main_image,
                                         )
            newUserProduct.save()
            messages.success(request, 'Məhsulunuz satışa çıxdı.')
            return render(request, 'forms/sell.html', context)
    return render(request, 'forms/sell.html', context)

@login_required(login_url='/login/')
def delete_product(request, id):
    product = Product.objects.all().filter(pk=id)
    product.delete()
    return redirect('account')

@login_required(login_url='/login/')
def addcomment(request, id):
    url = request.META.get('HTTP_REFERER')
    category = Category.objects.all()
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        good_sides = request.POST.get('good_sides')
        bad_sides = request.POST.get('bad_sides')
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        if good_sides == '' and bad_sides == '' and comment == '':
            messages.warning(request, 'Boş rəy yazmaq mümkün deyil')
        else:
            cat = Product.objects.get(pk=id)
            newComment = ProductComment(product=cat,
                                        user=request.user,
                                        rating=rating,
                                        good_sides=good_sides,
                                        bad_sides=bad_sides,
                                        comment=comment)
            newComment.save()
            messages.success(request, 'Rəyiniz göndərildi')
            #return render(request, 'detail.html', {'category': category, 'product': product})
            return HttpResponseRedirect(url)
    return render(request, 'detail.html', {'category': category, 'product': product})


#Add to cart
def add_to_cart(request):
    #del request.session['cartdata']
    cart_p = {}
    cart_p[str(request.GET['id'])] = {
        'id': request.GET['id'],
        'name': request.GET['name'],
        'image': request.GET['image'],
        'slug': request.GET['slug'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'brand': request.GET['brand'],
        'sale': request.GET['sale'],
    }
    if 'cartdata' in request.session:
        if str(request.GET['id']) in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_p[str(request.GET['id'])]['qty'])
            cart_data.update(cart_p)
            request.session['cartdata'] = cart_data
        else:
            cart_data = request.session['cartdata']
            cart_data.update(cart_p)
            request.session['cartdata'] = cart_data

    else:
        request.session['cartdata'] = cart_p

    totalprice = 0
    for p_id, item in request.session['cartdata'].items():
        totalprice += float(item['price'])*int(item['qty'])

    return JsonResponse({'data': request.session['cartdata'], 'totalitems': len(request.session['cartdata']), 'totalprice': totalprice})


def shopcart(request):
    # Check product id's and convert to str
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    try:
        total_price = dict()
        subtotal = 0
        for values in request.session['cartdata'].items():
            total_price.update({values[0]: int(values[1]['qty']) * float(values[1]['price'])})
            subtotal += int(values[1]['qty'])*float(values[1]['price'])
    except KeyError:
        if request.user:
            messages.warning(request, 'Səbət boşdur!')
            return redirect('index')
        else:
            return redirect('login')
    category = Category.objects.all()
    context = {
        'products': id_list,
        'total_price': total_price,
        'subtotal': subtotal,
        'category': category,
        'cart_data': request.session['cartdata'],
        'totalitems': len(request.session['cartdata']),
    }
    return render(request, 'shopcart.html', context)


def delete_cart_item(request):
    category = Category.objects.all()
    p_id = request.GET['id']
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            del request.session['cartdata'][p_id]
            request.session['cartdata'] = cart_data
    subtotal = 0
    total_price = dict()
    for p_id,item in request.session['cartdata'].items():
        subtotal += int(item['qty'])*float(item['price'])
        total_price.update({p_id: int(item['qty']) * float(item['price'])})

        # Check sale
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    t = render_to_string('cart-list.html', {'cart_data': request.session['cartdata'],
                                            'totalitems': len(request.session['cartdata']),
                                            'subtotal': subtotal,
                                            'total_price': total_price,
                                            'products': id_list,
                                            'category': category})
    return JsonResponse({'data': t})



def update_cart_item(request):
    category = Category.objects.all()
    p_id = request.GET['id']
    p_qty = request.GET['qty']
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = p_qty
            request.session['cartdata'] = cart_data
    subtotal = 0
    total_price = dict()
    for p_id,item in request.session['cartdata'].items():
        subtotal += int(item['qty'])*float(item['price'])
        total_price.update({p_id: int(item['qty']) * float(item['price'])})

        # Check sale
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    t = render_to_string('cart-list.html', {'cart_data': request.session['cartdata'],
                                            'totalitems': len(request.session['cartdata']),
                                            'subtotal': subtotal,
                                            'total_price': total_price,
                                            'products': id_list,
                                            'category': category})
    return JsonResponse({'data': t})


def cleanCart(request):
    del request.session['cartdata']
    return redirect('index')

#Add to wishlist
def add_to_wishlist(request):
    wish_p = {}
    wish_p[str(request.GET['id'])] = {
        'id': request.GET['id'],
        'name': request.GET['name'],
        'image': request.GET['image'],
        'slug': request.GET['slug'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'brand': request.GET['brand'],
        'sale': request.GET['sale'],
    }
    if 'wishdata' in request.session:
        if str(request.GET['id']) in request.session['wishdata']:
            wish_data = request.session['wishdata']
            wish_data[str(request.GET['id'])]['qty'] = int(wish_p[str(request.GET['id'])]['qty'])
            wish_data.update(wish_p)
            request.session['wishdata'] = wish_data
        else:
            wish_data = request.session['wishdata']
            wish_data.update(wish_p)
            request.session['wishdata'] = wish_data

    else:
        request.session['wishdata'] = wish_p

    totalprice = 0
    for p_id, item in request.session['wishdata'].items():
        totalprice += float(item['price'])*int(item['qty'])

    return JsonResponse({'data': request.session['wishdata'], 'totalwish': len(request.session['wishdata']), 'totalprice': totalprice})


def wishlist(request):
    # Check product id's and convert to str
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    try:
        total_price = dict()
        subtotal = 0
        for values in request.session['wishdata'].items():
            total_price.update({values[0]: int(values[1]['qty']) * float(values[1]['price'])})
            subtotal += int(values[1]['qty'])*float(values[1]['price'])
    except KeyError:
        if request.user:
            messages.warning(request, 'Istəklər siyahısı boşdur!')
            return redirect('index')
        else:
            return redirect('login')
    category = Category.objects.all()
    context = {
        'products': id_list,
        'total_price': total_price,
        'subtotal': subtotal,
        'category': category,
        'wish_data': request.session['wishdata'],
        'totalwish': len(request.session['wishdata']),
    }
    return render(request, 'wishlist.html', context)


def delete_wishlist_item(request):
    category = Category.objects.all()
    p_id = request.GET['id']
    if 'wishdata' in request.session:
        if p_id in request.session['wishdata']:
            wish_data = request.session['wishdata']
            del request.session['wishdata'][p_id]
            request.session['wishdata'] = wish_data
    subtotal = 0
    total_price = dict()
    for p_id,item in request.session['wishdata'].items():
        subtotal += int(item['qty'])*float(item['price'])
        total_price.update({p_id: int(item['qty']) * float(item['price'])})

        # Check sale
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    t = render_to_string('wish-list.html', {'wish_data': request.session['wishdata'],
                                            'totalwish': len(request.session['wishdata']),
                                            'subtotal': subtotal,
                                            'total_price': total_price,
                                            'products': id_list,
                                            'category': category})
    return JsonResponse({'data': t})




#Add to compare
def add_to_compare(request):
    compare_p = {}
    compare_p[str(request.GET['id'])] = {
        'id': request.GET['id'],
        'name': request.GET['name'],
        'image': request.GET['image'],
        'slug': request.GET['slug'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'brand': request.GET['brand'],
        'sale': request.GET['sale'],
        'stock': request.GET['stock'],
        'description': request.GET['description'],
    }
    if 'comparedata' in request.session:
        if str(request.GET['id']) in request.session['comparedata']:
            compare_data = request.session['comparedata']
            compare_data[str(request.GET['id'])]['qty'] = int(compare_p[str(request.GET['id'])]['qty'])
            compare_data.update(compare_p)
            request.session['comparedata'] = compare_data
        else:
            compare_data = request.session['comparedata']
            compare_data.update(compare_p)
            request.session['comparedata'] = compare_data

    else:
        request.session['comparedata'] = compare_p

    totalprice = 0
    for p_id, item in request.session['comparedata'].items():
        totalprice += float(item['price'])*int(item['qty'])

    return JsonResponse({'data': request.session['comparedata'], 'totalcompare': len(request.session['comparedata']), 'totalprice': totalprice})


def compare(request):
    # Check product id's and convert to str
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    try:
        total_price = dict()
        subtotal = 0
        for values in request.session['comparedata'].items():
            total_price.update({values[0]: int(values[1]['qty']) * float(values[1]['price'])})
            subtotal += int(values[1]['qty'])*float(values[1]['price'])
    except KeyError:
        if request.user:
            messages.warning(request, 'Müqayisə siyahısı boşdur!')
            return redirect('index')
        else:
            return redirect('login')
    category = Category.objects.all()
    context = {
        'products': id_list,
        'total_price': total_price,
        'subtotal': subtotal,
        'category': category,
        'compare_data': request.session['comparedata'],
        'totalcompare': len(request.session['comparedata']),
    }
    return render(request, 'compare.html', context)


def delete_compare_item(request):
    category = Category.objects.all()
    p_id = request.GET['id']
    if 'comparedata' in request.session:
        if p_id in request.session['comparedata']:
            compare_data = request.session['comparedata']
            del request.session['comparedata'][p_id]
            request.session['comparedata'] = compare_data
    subtotal = 0
    total_price = dict()
    for p_id,item in request.session['comparedata'].items():
        subtotal += int(item['qty'])*float(item['price'])
        total_price.update({p_id: int(item['qty']) * float(item['price'])})

        # Check sale
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    t = render_to_string('compare-list.html', {'compare_data': request.session['comparedata'],
                                            'totalcompare': len(request.session['comparedata']),
                                            'subtotal': subtotal,
                                            'total_price': total_price,
                                            'products': id_list,
                                            'category': category})
    return JsonResponse({'data': t})

def cleanCompare(request):
    del request.session['comparedata']
    messages.success(request, 'Müqayisə siyahısı təmizləmdi!')
    return redirect('index')



def search(request):
    category = Category.objects.all()
    keywords = request.GET.get('keywords')
    category_name = request.GET.get('category_name')
    if category_name not in Category.objects.values_list('name', flat=True):
        if keywords:
            products = Product.objects.filter(name__contains=keywords)
            return render(request, 'search.html', {'products': products, 'category': category})
    else:
        if keywords:
            products = Product.objects.filter(name__contains=keywords, category__name=category_name)
            return render(request, 'search.html', {'products': products, 'category': category})

    return render(request, 'products.html', {'category': category})

@login_required(login_url='/login/')
def checkout(request):
    products = Product.objects.filter(sale__gte=0).values_list('id')
    id_list = list()
    for id in products:
        for id in id:
            id_list.append(str(id))

    try:
        total_price = dict()
        subtotal = 0
        for values in request.session['cartdata'].items():
            total_price.update({values[0]: int(values[1]['qty']) * float(values[1]['price'])})
            subtotal += int(values[1]['qty'])*float(values[1]['price'])
    except KeyError:
        if request.user:
            messages.warning(request, 'Səbət boşdur!')
            return redirect('index')
        else:
            return redirect('login')
    category = Category.objects.all()
    context = {
        'products': id_list,
        'total_price': total_price,
        'subtotal': subtotal,
        'category': category,
        'cart_data': request.session['cartdata'],
        'totalitems': len(request.session['cartdata']),
    }
    return render(request, 'checkout.html', context)


def payment(request):
    category = Category.objects.all()
    context = {
        'category': category
    }
    if request.method == 'POST':
        cardname = request.POST.get('cardname')
        cardnumber = request.POST.get('cardnumber')
        expmonth = request.POST.get('expmonth')
        expyear = request.POST.get('expyear')
        cvv = request.POST.get('cvv')
        fullname = request.user.get_full_name()
        email = request.user.email
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip = request.POST.get('zip')

        newCheckout = Checkout(cardname=cardname,
                                cardnumber = cardnumber,
                                expmonth = expmonth,
                                expyear = expyear,
                                cvv = cvv,
                                fullname = fullname,
                                email = email,
                                address = address,
                                city = city,
                                state = state,
                                zip = zip)
        newCheckout.save()

        for id in request.session['cartdata']:
            newSold = Sold(checkout = newCheckout,
                           product = id )
            newSold.save()
        messages.success(request, 'Ödəniş tamamlandı')
        return redirect('cleancart')
    return render(request, 'checkout.html', context)


def brandFilter(request, brand_slug):
    category = Category.objects.all()
    products = Product.objects.all().filter(brand=Brand.objects.get(slug=brand_slug))
    sidebar = Product.objects.all().order_by('?')[:4]
    brands = Brand.objects.all()
    context = {
        'category': category,
        'products': products,
        'sidebar':sidebar,
        'brands':brands,
    }

    return render(request, 'products.html', context)