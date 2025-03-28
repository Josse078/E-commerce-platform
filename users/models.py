from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank = True)
    
    def __str__(self):
        return self.name