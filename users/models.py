from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    stock = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank = True)
    
    def __str__(self):
        return self.name
class CartItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    def __str__(self):
        return f'{self.product.name}(x{self.quantity})'
    def total_price(self):
        return self.product.price * self.quantity

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    paypal_email = models.EmailField(max_length=255,blank=True,null=True)
    def __str__(self):
        return self.user.username