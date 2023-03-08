from django.db import models

class UserDetail(models.Model):
    uname=models.CharField(unique=True, max_length=50)
    uemail=models.CharField(max_length=50)
    uphone=models.CharField(max_length=50, null=True)
    upassword=models.CharField(max_length=50)
    uactive=models.BooleanField(default=True)
    uimage = models.ImageField(upload_to='imagestore/', null=True, blank=True)
    uotp=models.IntegerField(null=True)
    def __str__(self): 
        return self.uname 

class Category(models.Model):
    name = models.CharField(max_length=50)
    offer_active = models.BooleanField(default=False)
    discount = models.IntegerField(null=True,blank=True)
    def __str__(self):
        return self.name      

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='imagestore/')
    stock = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default='Wired')
    normalprice = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    
    @property
    def price(self):
        if self.category.discount is None:
            return int(self.normalprice)
        else:  
            return int(self.normalprice)-int(self.category.discount)
    
class Coupon(models.Model):
    coupon_code=models.CharField(max_length=30)
    is_active=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=0)
    minimum_amount=models.IntegerField(default=500)
    applied=models.BooleanField(default=False)
    user=models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False)
    def __str__(self):
        return self.coupon_code
    
class Cart(models.Model):
    cartid=models.AutoField(primary_key=True)
    user=models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False)

class CartItem(models.Model):
    cartitemid=models.AutoField(primary_key=True)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=False)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=False)
    quantity=models.PositiveBigIntegerField()

    @property
    def subtotal(self):
        return int(self.product.price)*int(self.quantity)

STATE_CHOICES = (
    ('KARNATAKA', 'KARNATAKA'),
    ('KERALA', 'KERALA'),
    ('TAMIL NADU', 'TAMIL NADU'),
    ('GOA', 'GOA'),
    ('GUJARAT', 'GUJARAT')
)
   
    
class Address(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=12)
    housename = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50, default='KERALA')
    selected = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
    ('Cancel Requested', 'Cancel Requested'),
    ('Return Requested', 'Return Requested'),
    ('Cancelled', 'Cancelled'),
    ('Returned', 'Returned'),
)
TYPE_CHOICES = (
    ('Cash on delivery', 'Cash on delivery'),
    ('Paypal', 'Paypal'),
    ('Razorpay', 'Razorpay'),
)
class Order(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordertype = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Cash on delivery')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return str(self.id)

    
class Wishlist(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE,default=None)
    product = models.ForeignKey(Product,  on_delete=models.CASCADE,default=None)
    def __str__(self):
        return (str(self.user.uname) + str(" , ") +str(self.product.name))

class Banner(models.Model):
    name = models.CharField(max_length=30,default=None)
    image = models.ImageField(upload_to='imagestore/banner',default=None)
    def __str__(self):
        return self.name
