from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    paypal_email = forms.EmailField(required=False,help_text='Optional. Enter your PayPal email for receiving payments.')
    class Meta:
        model = User
        fields = ['username', 'email','paypal_email', 'password1', 'password2']
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','description','price','image','stock']
