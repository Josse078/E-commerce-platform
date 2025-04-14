from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from .forms import UserRegisterForm, ProductForm,ProfileUpdateForm,UserRegisterForm
from django.contrib import messages
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product,CartItem,Profile
from collections import defaultdict
from paypalrestsdk import Payment
from django import template
import paypalrestsdk
from django.conf import settings
register = template.Library()
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id":settings.PAYPAL_CLIENT_ID,
    "client_secret":settings.PAYPAL_CLIENT_SECRET,
})

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
@login_required
def home(request):
    products = Product.objects.all()[:10]
    return render(request,'users/home.html',{'products':products})
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            paypal_email = form.cleaned_data.get('paypal_email')
            Profile.objects.create(user=user,paypal_email=paypal_email)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request,'users/register.html',{'form':form})
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
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

@login_required
def user_logout(request):
    logout(request)
    messages.info(request,"You have successfully logged out")
    return redirect('login')

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST,instance=request.user)
        profile_form = ProfileUpdateForm(request.POST,instance = request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your profile has been updated successfully')
            return redirect('profile')
    else:
        user_form = UserRegisterForm(instance=request.user)
        Profile.objects.get_or_create(user=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form
    }
    return render(request,'users/Profile.html',context)



# @login_required
# def view_cart(request):
#     cart_items = CartItem.objects.filter(user=request.user)
#     print(cart_items)
#     cart_by_seller = defaultdict(list)
#     seller_totals = {}
#     for item in cart_items:
#         print(item.product,item.product.seller)
#         seller = item.product.seller
#         cart_by_seller[seller].append(item)
#         if seller not in seller_totals:
#             seller_totals[seller] = 0
#         seller_totals[seller] += item.total_price()
#     total = sum(item.total_price() if callable(item.total_price) else item.total_price for item in cart_items)
#     context = {
#         'cart_items' : cart_items,
#         'cart_by_seller' : cart_by_seller,
#         'seller_totals' : seller_totals,
#         'total' : total,
#     }
#     print("Cart by seller: ", cart_by_seller)
#     return render(request,'Commerce/cart.html',context)

@login_required
def view_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.total_price() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'Commerce/cart.html', context)
@login_required
def remove_from_cart(request,item_id):
    cart_item = get_object_or_404(CartItem,id=item_id,user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def add_to_cart(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    cart_item,created = CartItem.objects.get_or_create(user=request.user,product=product)   
    if not created and cart_item.quantity >= product.stock:
        messages.error(request,'Product out of stock')
        return redirect('view_cart')
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    if cart_item.quantity > product.stock:
        cart_item.quantity = product.stock
    cart_item.save()
    messages.success(request,f'{product.name} added to your cart')
    return redirect('view_cart')

# @login_required
# def checkout_seller(request,seller_id):
#     cart_items = CartItem.objects.filter(user=request.user,product__seller_id=seller_id)
#     if not cart_items.exists():
#         return render(request,'cart.html',{"error":"Your cart is empty"})
#     total_amount = sum(item.total_price for item in cart_items)
#     seller = cart_items.first().product.seller
#     payment = Payment({
#         "intent": "sale",
#         "payer" : {
#             "payment_method": "paypal"
#         },
#         "redirect_urls":{
#             "return_url":request.build_absolute_uri('/payment/execute/'),
#             "cancel_url":request.build_absolute_uri('/payment/cancel')
#         },
#         "transactions": [{
#             "payee":{
#                 "email": seller.profile.paypal_email
#             },
#             "item_list":{
#                 "items":[{
#                     "name": item.product.name,
#                     "sku": item.product.sku,
#                     "price": str(item.product.price),
#                     "currency":"USD",
#                     "quantity":item.quality
#                 }for item in cart_items]
#             },
#             "amount":{
#                 "total": str(total_amount),
#                 "currency":"USD"
#             },
#             "description": f"Payment to {seller.username}"
#         }]
#     })
#     if payment.create():
#         for link in payment.links:
#             if link.method == "REDIRECT":
#                 return redirect(link.href)
#     else:
#         return render(request,"payment_error.html",{"error":payment.error})

@login_required
def checkout_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    total_amount = cart_item.total_price()
    seller = cart_item.product.seller

    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/payment/execute/'),
            "cancel_url": request.build_absolute_uri('/payment/cancel/')
        },
        "transactions": [{
            "payee": {
                "email": seller.profile.paypal_email
            },
            "item_list": {
                "items": [{
                    "name": cart_item.product.name,
                    "sku": cart_item.product.sku,
                    "price": str(cart_item.product.price),
                    "currency": "USD",
                    "quantity": cart_item.quantity
                }]
            },
            "amount": {
                "total": str(total_amount),
                "currency": "USD"
            },
            "description": f"Payment to {seller.username} for {cart_item.product.name}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        return render(request, "payment_error.html", {"error": payment.error})

@login_required
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        transaction = payment.transactions[0]
        item_name = transaction.item_list.items[0].name
        cart_item = get_object_or_404(CartItem, product__name=item_name, user=request.user)
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()
        cart_item.delete()
        return render(request,'payment_success.html')
    else:
        return render(request,'payment_error.html')

def payment_done(request):
    return render(request,'payment_done.html')
def payment_cancel(request):
    return render(request,'payment_cancel.html')
