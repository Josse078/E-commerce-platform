from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, ProductForm
from django.contrib import messages
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
@login_required
def home(request):
    products = Product.objects.all()[:10]
    return render(request,'users/home.html',{'products':products})
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request,'users/register.html',{'form':form})
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                messages.info(request,f'You are now logged in as {username}')
                return redirect('home')
            else:
                messages.error(request,'Invalid username or password')
        else:
            messages.error(request,'Invalid username or password')
    else:
        form = AuthenticationForm()
        return render(request,'users/login.html',{'form':form})
@login_required
def sell_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request,'Commerce/sell.html',{'form':form})
    
def user_products(request):
    user = request.user
    products = Product.objects.filter(seller=user)
    return render(request,'Commerce/products.html',{'products':products})

@login_required
def delete_product(request,product_id):
    product = get_object_or_404(Product,id=product_id,seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('user_products')
    return render(request,'Commerce/delete_confirm.html',{'product':product})
