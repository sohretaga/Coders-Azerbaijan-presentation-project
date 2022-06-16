from product.models import Category, Product
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect



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
