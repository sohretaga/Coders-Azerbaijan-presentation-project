from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from product.models import Category, Product, CustomUser
from pages.models import Contact
from django.db.utils import IntegrityError


# Create your views here.


def index(request):
    category = Category.objects.all()
    products = Product.objects.all().order_by('?')
    new_products = Product.objects.all().order_by('-date_created')[:4]
    best_products = Product.objects.all().filter(bestseller=True).order_by('?')[:4]
    for_you = Product.objects.all().order_by('?')[:8]
    context = {'category': category,
               'products': products,
               'new_products': new_products,
               'best_products': best_products,
               'for_you': for_you,}
    return render(request, 'index.html', context)

def about(request):
    category = Category.objects.all()
    context = {'category': category}
    return render(request, 'about.html', context)

def contact(request):
    url = request.META.get('HTTP_REFERER')
    category = Category.objects.all()
    context = {'category': category}
    if request.POST:
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if full_name == '' or message == '':
            messages.warning(request, 'Bütün xanaları doldurduğunuzdan əmin olun!')
        else:
            newMessage = Contact(full_name=full_name, email=email, message=message)
            newMessage.save()
            messages.success(request, 'Mesajınız uğurla göndərildi! Sizinlə əlaqə saxlanılacaq.')
        return HttpResponseRedirect(url)
    return render(request, 'forms/contact.html', context)

def userRegister(request):
    category = Category.objects.all()
    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        
        try:
            newUser = CustomUser.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, user_phone=phone)
            newUser.set_password(password)
            newUser.save()
            messages.success(request, 'Qeydiyyat uğurla tamamlandı!')
            return render(request, 'forms/register.html', {'category': category})
        except IntegrityError:
            messages.warning(request, 'Qeydiyyat uğursuz oldu')
            return render(request, 'forms/register.html', {'category': category})
    return render(request, 'forms/register.html', {'category': category})

def userLogin(request):
    category = Category.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Giriş edildi!')
            return redirect('index')
        else:
            messages.warning(request, 'email vəya şifrə yanlışdılr!')
            return redirect('login')
    return render(request, 'forms/login.html', {'category': category})

def userLogot(request):
    logout(request)
    return redirect('index')

def account(request):
    category = Category.objects.all()
    account = User.objects.all()
    products = Product.objects.all().filter(user_id=request.user.id, used=True)
    context = {'account': account,
               'category': category,
               'products': products}
    return render(request, 'account.html', context)


