from django.db import models

from base.models import BaseModel
from django.contrib.auth.models import *
from django.core.validators import *
from django.dispatch import receiver
from django.db.models.signals import post_save
import uuid
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import *
from django.contrib.auth import get_user_model


class Category(BaseModel):
    category_name=models.CharField(max_length=255)
    slug = models.SlugField(unique=True  , null=True , blank=True)
   
    category_description=models.TextField()
    add_date = models.DateTimeField(auto_now_add=True,null=True)
    
    def save(self , *args , **kwargs):
        self.slug = slugify(self.category_name)
        super(Category ,self).save(*args , **kwargs)
    def __str__(self):
        return self.category_name


class Product(BaseModel):
    
    product_name=models.CharField(max_length=255)
    product_description=models.TextField()
    price=models.IntegerField()
    slug = models.SlugField(unique=True  , null=True , blank=True)
    category =models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    availability=models.BooleanField(default=False)
   

    upload_date = models.DateTimeField(auto_now_add=True)  # Added field for upload date
    video_file = models.FileField(upload_to='videos/',default="./media/videos/video.mp4")  # Added field for video file, specify upload directory as needed

    def __str__(self):
        return self.product_name

 
    def save(self , *args , **kwargs):
        self.slug = slugify(self.product_name)
        super(Product ,self).save(*args , **kwargs)
        
        
class Order(BaseModel):

    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='orders')
    
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.product} for {self.quantity} of {self.product.product_name} on {self.order_date}"
    
     
 
    def save(self, *args, **kwargs):
        # Update the slug based on the product's name
        self.slug = slugify(self.product.product_name)
        super(Order, self).save(*args, **kwargs)
        
        
        
class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    isPaid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    razor_pay_order_id = models.CharField(max_length=100,null=True,blank=True)
    razor_pay_payment_id = models.CharField(max_length=100,null=True,blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return f"Cart item for {self.user.username}: {self.product.product_name}"       
    
    
class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True,default="")
    
    
    def __str__(self):
        return self.name
    
    
class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions',
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAYME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)
    
class Paytm_history(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rel_payment_paytm', on_delete=models.CASCADE, null=True, default=None)
    MERC_UNQ_REF = models.IntegerField('USER ID')
    ORDERID = models.CharField('ORDER ID', max_length=30)
    TXNDATE = models.DateTimeField('TXN DATE', default=timezone.now)
    TXNID = models.CharField('TXN ID', max_length=100)
    BANKTXNID = models.CharField('BANK TXN ID', max_length=100, null=True, blank=True)
    BANKNAME = models.CharField('BANK NAME', max_length=50, null=True, blank=True)
    RESPCODE = models.IntegerField('RESP CODE')
    PAYMENTMODE = models.CharField('PAYMENT MODE', max_length=10, null=True, blank=True)
    CURRENCY = models.CharField('CURRENCY', max_length=4, null=True, blank=True)
    GATEWAYNAME = models.CharField("GATEWAY NAME", max_length=30, null=True, blank=True)
    MID = models.CharField(max_length=40)
    RESPMSG = models.TextField('RESP MSG', max_length=250)
    TXNAMOUNT = models.FloatField('TXN AMOUNT')
    STATUS = models.CharField('STATUS', max_length=12)

    # class Meta:
    #     app_label = 'paytm'

    def __str__(self):
        return '%s  (%s)' % (self.user.username ,self.pk)


    def __unicode__(self):
        return self.STATUS


    def __iter__(self):
        for field_name in [f.name for f in self._meta.get_fields()]:
            value = getattr(self, field_name, None)
            yield (field_name, value)    
            
            
class EmailVerification(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    
    @classmethod
    def create(cls, user, otp):
        return cls.objects.create(user=user, otp=otp)
    
    def __str__(self):
        return f"{self.user.username} - {self.otp}"
    
class Profile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)   
    forget_password_token = models.CharField(max_length=150) 
    created_at = models.DateTimeField( auto_now_add=True)       
    
    def __str__(self):
        return self.user.username
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)    
class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    # Define the field to be used as the username
    USERNAME_FIELD = 'email'
    # Define additional fields required when creating a superuser
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        # Handle custom permissions logic if needed
        return True

    def has_module_perms(self, app_label):
        # Handle custom permissions logic if needed
        return True
    
class CustomUserEmailVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    
    @classmethod
    def create(cls, user, otp):
        return cls.objects.create(user=user, otp=otp)
    
    def __str__(self):
        return f"{self.user.email} - {self.otp}"    