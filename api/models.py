from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.BooleanField(default=True)
    sold_count = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')  # Fixed from stagory_id to category
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.product_name

class ProductTag(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('product', 'tag')

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # ADD THIS FIELD
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.utils import timezone
            import datetime
            self.expires_at = timezone.now() + datetime.timedelta(days=30)
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('user', 'product', 'status')

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_image = models.ImageField(upload_to='payments/', blank=True, null=True)
    name = models.CharField(max_length=200)
    payment_image = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, default='completed')  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.user.username}"

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    product_name = models.CharField(max_length=200)
    product_image = models.ImageField(upload_to='orders/', blank=True, null=True)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    payment_image = models.ImageField(upload_to='order_payments/', blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    cancellation_reason = models.TextField(blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

class Bank(models.Model):
    id = models.AutoField(primary_key=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.full_name