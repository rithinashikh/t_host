from django.shortcuts import render, redirect
from phase.forms.user import UserSignupForm, UserLoginForm, UserAddressForm, OrderForm
from phase.forms.product import ProductForm, CouponForm, BannerForm
from phase.forms.category import CategoryForm
# from phase.forms.coupon import CouponForm 
from .models import UserDetail, Product, Category, Cart, CartItem, Address, Order, Coupon, Wishlist, Banner
from django.contrib.auth.models import User
import requests, random
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.db.models.functions import ExtractMonth, ExtractDay
from django.db.models import Count
import calendar
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import TableStyle,Table
from reportlab.lib import colors
from datetime import datetime, time, timedelta
from django.http import FileResponse
from django.views import View
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import os 
import datetime

def index(request):
    obj = Banner.objects.all()
    return render(request, 'index.html',{'obj':obj})

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

class UserLoginView(View):
    def get(self, request):
        if 'uname' in request.session:
            return redirect('shop')
        else:
            fm = UserLoginForm()
            return render(request, 'userlogin.html', {'fm': fm})
    
    def post(self, request):
        uname = request.POST.get('uname')
        password = request.POST.get('upassword')
        customer = UserDetail.objects.filter(uname=uname).first()
        if customer and customer.upassword == password and customer.uactive:
            request.session['uname'] = uname
            return redirect('shop')
        else:
            return redirect('userlogin')
        
class UserSignupView(View):
    def get(self, request):
        if 'uname' in request.session:
            return redirect('shop')
        fm = UserSignupForm()
        return render(request, 'usersignup.html', {'fm': fm})
    
    def post(self, request):
        if 'uname' in request.session:
            return redirect('shop')
        fm = UserSignupForm(request.POST, request.FILES)
        if fm.is_valid():
            c_password = request.POST.get('c_password2')
            password = request.POST.get('upassword')
            if c_password == password:
                fm.save()
                return redirect('userlogin') 
            else:
                messages.warning(request, "Passwords are not matching")
                return redirect('usersignup') 
        else:
            return render(request, 'usersignup.html', {'fm': fm})



def shop(request):
    if 'uname' in request.session:
        cat=Category.objects.all()
        cat_id = request.GET.get('cat_id')
        if cat_id is not None:
            details3=Product.objects.filter(category__id=cat_id)          
        else:
            details3=Product.objects.all()
        paginator = Paginator(details3, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'shop.html', {'page_obj': page_obj,'cat':cat})
    else:
         return redirect('userlogin')

def shopsingle(request):
    if 'uname' in request.session:
        uid=request.GET['uid']
        details4=Product.objects.filter(id=uid).first()
        return render(request, 'shopsingle.html', {'mymembers4': details4})
    else:
        return render(request, 'userlogin.html')
    
class AdminLoginView(View):
    def get(self, request):
        if 'username' in request.session:
            return redirect('admindashboard')
        else:
            return render(request, 'adminlogin.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return redirect('admindashboard')
        else:
            return render(request, 'adminlogin.html')

def admindashboard(request):
    if 'username' in request.session:
        orders_months = Order.objects.annotate(month=ExtractMonth("ordered_date")).values('month').annotate(count=Count('id')).values('month','count')
        months = []
        total_ord = []
        for i in orders_months:
            months.append(calendar.month_name[i['month']])
            total_ord.append(i['count'])
            order = Order.objects.order_by('ordered_date')[:2]
        return render(request, 'admindashboard.html',{'months':months,'total_ord':total_ord})
    
    else:
        return render(request, 'adminlogin.html')

    
def adminlogout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('adminlogin')

def adminuserlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=UserDetail.objects.filter(uname__icontains=search)
        else:
            member=UserDetail.objects.all().order_by('-id')
        paginator = Paginator(member, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'adminuserlist.html',{'page_obj': page_obj})
    else:
        return render(request, 'adminlogin.html')
    

def adminproductlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=Product.objects.filter(name__icontains=search)
        else:
            member=Product.objects.all().order_by('-id')
        paginator = Paginator(member, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'adminproductlist.html',{'page_obj': page_obj})
    else:
        return render(request, 'adminlogin.html')
    
class AdminAddProductView(View):
    def get(self, request):
        if 'username' in request.session:
            fm = ProductForm()
            return render(request, 'adminaddproduct.html', {'fm': fm})
        else:
            return redirect('adminlogin')
    
    def post(self, request):
        fm = ProductForm(request.POST, request.FILES)
        if fm.is_valid():
            fm.save()
            return redirect('adminproductlist')
        else:
            return render(request, 'adminaddproduct.html', {'fm': fm})

class AdminAddCategoryView(View):
    def get(self, request):
        if 'username' in request.session:
            fm = CategoryForm()
            return render(request, 'adminaddcategory.html', {'fm': fm})
        else:
            return render(request, 'adminlogin.html')

    def post(self, request):
        if 'username' in request.session:
            fm = CategoryForm(request.POST, request.FILES)
            if fm.is_valid():
                name = fm.cleaned_data['name']
                dup = Category.objects.filter(name=name).first()
                if dup:
                    messages.warning(request, 'Category already exists')
                    return redirect('adminaddcategory')
                else:
                    fm.save()
                    return redirect('admincategorylist')
            else:
                fm = CategoryForm()
                return render(request, 'adminaddcategory.html', {'fm': fm})
        else:
            return render(request, 'adminlogin.html')


def updateproduct(request,id):
    if 'username' in request.session:
        prod = Product.objects.get(id=id)
        if request.method == 'POST':
            fm = ProductForm(request.POST, request.FILES, instance=prod)
            if fm.is_valid():
                fm.save()
                messages.success(request,"Product details updated")
                return redirect('adminproductlist')
            else:
                return render(request, 'adminupdateproduct.html', {'fm': fm})
        else:
            fm = ProductForm(instance=prod)
            return render(request, 'adminupdateproduct.html', {'fm': fm})
    else:
        return redirect('adminlogin')

def userblock(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        block_check=UserDetail.objects.filter(id=uid)
        for x in block_check:
            if x.uactive:
                UserDetail.objects.filter(id=uid).update(uactive=False)
                messages.warning(request, f'{x.uname} is blocked')
            else:
                UserDetail.objects.filter(id=uid).update(uactive=True)
                messages.success(request, f'{x.uname} is unblocked')
        return redirect('adminuserlist')
    else:
        return redirect('adminlogin')


def userlogout(request):
    if 'uname' in request.session:
        del request.session['uname']
    return redirect('userlogin')


def deleteproduct(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Product.objects.filter(id=uid).delete()
        return redirect('adminproductlist')
    else:
        return redirect('adminlogin')

def admincategorylist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=Category.objects.filter(name__icontains=search)
        else:
            member=Category.objects.all().order_by('-id')
        paginator = Paginator(member, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admincategorylist.html',{'page_obj': page_obj})
    else:
        return render(request, 'adminlogin.html')
    

    
def deletecategory(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Category.objects.filter(id=uid).delete()
        return redirect('admincategorylist')
    else:
        return redirect('adminlogin')
    
class UpdateCategoryView(View):
    def get(self, request):
        if 'username' in request.session:
            uid = request.GET['uid']
            cat = Category.objects.get(id=uid)
            fm = CategoryForm(instance=cat)
            return render(request, 'adminupdatecategory.html', {'fm': fm})
        else:
            return redirect('adminlogin')
    
    def post(self, request):
        if 'username' in request.session:
            uid = request.GET['uid']
            cat = Category.objects.get(id=uid)
            fm = CategoryForm(request.POST, request.FILES, instance=cat)
            if fm.is_valid():
                fm.save()
                return redirect('admincategorylist')
            else:
                return render(request, 'adminupdatecategory.html', {'fm': fm})
        else:
            return redirect('adminlogin')    
        
class UserOTPLoginView(View):
    def get(self, request):
        return render(request, 'userotplogin.html')
    def post(self, request):
        uname = request.POST.get('uname')
        request.session['some_data'] = uname
        return redirect('otplogin')
    
def otplogin(request):
    uname = request.session['some_data']
    try:
        obj = UserDetail.objects.get(uname=uname)
    except:
        messages.warning(request,"No user found")
        return redirect('userotplogin')
    if request.method=='POST':
        c_otp = int(request.POST.get('c_otp'))
        if c_otp== obj.uotp:
            request.session['uname'] = uname
            del request.session['some_data']
            messages.success(request, "Login completed successfully")
            return redirect('shop')
        else:
            messages.warning(request, "Incorrect OTP")
            return redirect('userotplogin')
    else:
        otp_sent = random.randint(1001, 9999)
        UserDetail.objects.filter(uname=uname).update(uotp=otp_sent) 
        # url = 'https://www.fast2sms.com/dev/bulkV2'
        # payload = f'sender_id=TXTIND&message={otp_sent}&route=v3&language=english&numbers={obj.uphone}'
        # headers = {
        #     'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
        #     'Content-Type': "application/x-www-form-urlencoded"
        #     }
        # response = requests.request("POST", url, data=payload, headers=headers)
        # print(response.text) 
        print("Sent value::",otp_sent)
    return render(request, 'otp.html')


def checkout(request):
    if 'uname' in request.session:
        if request.method=='POST':
            if 'addressform' in request.POST:
                fm = UserAddressForm(request.POST) 
                if fm.is_valid():
                    use = request.session['uname']
                    user = UserDetail.objects.get(uname = use)
                    reg = fm.save(commit=False)
                    reg.user = user
                    reg.save()
                    messages.success(request, 'new address added successfully')
                    return redirect('checkout') 
                else:
                    messages.warning(request,'Enter correct address') 
                    return render(request, 'checkout.html', {'fm': fm})
            elif 'couponform' in request.POST:
                check = request.POST.get('c_code')
                uname=request.session['uname']
                try:
                    obj = Coupon.objects.get(user__uname=uname,is_active=True)
                except:
                    messages.warning(request,'No coupon')
                    return redirect('checkout')
                if check==obj.coupon_code and obj.is_active:
                    Coupon.objects.filter(user__uname=uname).update(applied=True)
                elif check==obj.coupon_code:
                    messages.warning(request,'Coupon has expired') 
                else:
                    messages.warning(request,'Coupon is not valid')
                    # return redirect('checkout')
                return redirect('checkout')            
        else:
            fm = UserAddressForm()
            use = request.session['uname']
            context=Address.objects.filter(user__uname = use).order_by('-id')
            try:
                coup = Coupon.objects.get(user__uname=use,is_active=True,applied=True)
            except:
                coup = Coupon.objects.get(user__uname=use,is_active=True)
            ret = itemcalculate(use)
            disc = ret['datap']['total']
            applied_discount = disc - coup.discount_price
            return render(request, 'checkout.html', {'fm': fm, 'context': context, 'data':ret['data'], 'datap':ret['datap'],'coup':coup,'disc':applied_discount})
    else:
        return redirect('userlogin')

def updateaddress(request,id):
    if 'uname' in request.session:
        add = Address.objects.get(id=id)
        if request.method == 'POST':
            fm = UserAddressForm(request.POST, instance=add)
            if fm.is_valid():
                fm.save()
                messages.success(request,"Address updated successfully")
                return redirect('checkout')
        else:
            fm = UserAddressForm(instance=add)
            use = request.session['uname']
            context=Address.objects.filter(user__uname = use)
            ret = itemcalculate(use)
            return render(request, 'updateaddress.html', {'fm': fm, 'context': context, 'data':ret['data'], 'datap':ret['datap']})
    else:
        return redirect('userlogin')

def deleteaddress(request):
    if 'uname' in request.session:
        uid=request.GET['uid']
        Address.objects.filter(id=uid).delete()
        return redirect('checkout')
    else:
        return redirect('userlogin')

def address_select(request):
    if 'uname' in request.session:
        uid=request.GET['uid']
        select_check=Address.objects.filter(id=uid)
        for x in select_check:
            if x.selected:
                Address.objects.filter(id=uid).update(selected=False)
                messages.warning(request, f'{x.name} is Unselected')
            else:
                Address.objects.all().update(selected=False)
                Address.objects.filter(id=uid).update(selected=True)
                messages.success(request, f'{x.name} is Selected')
        return redirect('checkout')
    else:
        return redirect('userlogin')

def addtocart(request):
    if 'uname' in request.session:
        use=request.session['uname']
        user=UserDetail.objects.get(uname=use)
        try:
            cart=Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart=Cart.objects.create(user=user)
        try:
            pid=request.POST['pid']
        except:
            pid=request.GET.get('pid')
        try:
            product=Product.objects.get(id=pid)
        except Product.DoesNotExist:
            return redirect('shop')
        try:
            if product.stock < 1:
                messages.warning(request, 'Out of stock')
                return redirect('shop')
            else:
                cartitem=CartItem.objects.get(cart=cart,product=product)
                cartitem.quantity+=1
                product.stock-=1
                Product.objects.filter(id=pid).update(stock=product.stock)
        except CartItem.DoesNotExist:
            if product.stock < 1:
                messages.warning(request, 'Out of stock')
                return redirect('shop')
            else:
                cartitem=CartItem.objects.create(cart=cart,product=product,quantity=1)
                product.stock-=1
                Product.objects.filter(id=pid).update(stock=product.stock)
        cartitem.save()
        return redirect('cart')
    else:
        return redirect('userlogin')

def itemcalculate(name):
    total=0
    quantity=0
    set1=UserDetail.objects.filter(uname=name).first()
    set2=set1.id
    data=CartItem.objects.filter(cart__user__id=set2)
    datat=CartItem.objects.filter(cart__user__id=set2)
    for d in data:
        x=int(d.product.price)
        y=int(d.quantity)
        total += (x*y)
        quantity += d.quantity
    datap={
        "total":total,
        "quantity":quantity
    }
    return({'data':data, 'datap':datap})

def cart(request):
    if 'uname' in request.session:
        name=request.session['uname']
        ret = itemcalculate(name)
        return render(request,'cart.html',ret)
    else:
        return redirect('userlogin')

def delcartitems(request):
    if 'uname' in request.session:
        id=request.GET['id']
        it=CartItem.objects.get(cartitemid=id)
        cart_quantity = it.quantity
        cart_product = it.product.name
        Product.objects.filter(name=cart_product).update(stock=F('stock')+cart_quantity)
        CartItem.objects.filter(cartitemid=id).delete()
        return redirect('cart')
    else:
        return redirect('userlogin')

def paypal(request):
    if 'uname' in request.session:
        user = request.session['uname']
        use1 = UserDetail.objects.get(uname = user)
        use2 = Address.objects.get(user=use1,selected=True)
        cart = CartItem.objects.filter(cart__user__uname=use1)
        for c in cart:
            Order(user=use1, address=use2, product=c.product, amount=c.subtotal, ordertype= 'Paypal').save()
            c.delete()
        return render(request,'orderconfirm.html')
    else:
        return redirect('userlogin')



def order(request):
    if 'uname' in request.session:
        user = request.session['uname']
        user = UserDetail.objects.get(uname = user)
        ord = Order.objects.filter(user=user).order_by('-id')
        paginator = Paginator(ord, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'order.html',{'page_obj':page_obj})
    else:
        return redirect('userlogin')

def orderconfirm(request):
    if 'uname' in request.session:    
        user = request.session['uname']
        use1 = UserDetail.objects.get(uname = user)
        use2 = Address.objects.get(user=use1,selected=True)
        cart = CartItem.objects.filter(cart__user__uname=use1)
        try:
            coupon = Coupon.objects.get(user=use1,is_active=True,applied=True)
            discount = coupon.discount_price
        except:
            discount = 0
        cartcount = cart.count()
        for c in cart:
            Order(user=use1, address=use2, product=c.product, amount=c.subtotal-(discount)/cartcount).save()
            c.delete() 
        return render(request,'orderconfirm.html')
    else:
        return redirect('userlogin')

def plus_cart(request):
    if request.method == 'GET':
        use = request.session['uname']
        user = UserDetail.objects.get(uname = use)
        prod_id=request.GET['prod_id']
        c = CartItem.objects.get(Q(product=prod_id) & Q(cart__user=user))
        c.quantity+=1
        c.save()
        Product.objects.filter(id=prod_id).update(stock=F('stock') - 1)
        d = CartItem.objects.get(Q(product=prod_id) & Q(cart__user=user))
        sub = d.subtotal
        ret = itemcalculate(use)
        datap = {
            'total': ret['datap']['total'],
            'quantity': ret['datap']['quantity'],
            'ind_subtotal': sub,
        }
        return JsonResponse(datap)
    
def minus_cart(request):
    if request.method == 'GET':
        use = request.session['uname']
        user = UserDetail.objects.get(uname = use)
        prod_id=request.GET['prod_id']
        c = CartItem.objects.get(Q(product=prod_id) & Q(cart__user=user))
        c.quantity-=1
        c.save()
        Product.objects.filter(id=prod_id).update(stock=F('stock') + 1)
        d = CartItem.objects.get(Q(product=prod_id) & Q(cart__user=user))
        sub = d.subtotal
        ret = itemcalculate(use)
        datap = {
            'total': ret['datap']['total'],
            'quantity': ret['datap']['quantity'],
            'ind_subtotal': sub,
        }
        return JsonResponse(datap)
    
def cancelorder(request,id):
    if 'uname' in request.session:  
        Order.objects.filter(id=id).update(status='Cancel Requested')
        return redirect('order')
    else:
        return redirect('userlogin')

def returnorder(request,id):
    if 'uname' in request.session: 
        Order.objects.filter(id=id).update(status='Return Requested')
        return redirect('order')
    else:
        return redirect('userlogin')


def adminorderlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=Order.objects.filter(Q(user__uname__icontains=search)|Q(id__icontains=search)).order_by('-id')
        else:
            member = Order.objects.all().order_by('-id')
        paginator = Paginator(member, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'adminorderlist.html', {'page_obj': page_obj})
    else:
        return render('adminlogin')
    
class OrderUpdateView(View):
    def get(self, request, id):
        if 'username' in request.session:
            ord = Order.objects.get(id=id)
            fm = OrderForm(instance=ord)
            return render(request, 'adminupdateorder.html', {'fm': fm})
        else:
            return redirect('adminlogin')

    def post(self, request, id):
        if 'username' in request.session:
            ord = Order.objects.get(id=id)
            fm = OrderForm(request.POST, request.FILES, instance=ord)
            if fm.is_valid():
                fm.save()
                return redirect('adminorderlist')
            else:
                return render(request, 'adminupdateorder.html', {'fm': fm})
        else:
            return redirect('adminlogin')

def userprofile(request):
    if 'uname' in request.session:       
        user=request.session['uname']
        profile=UserDetail.objects.get(uname=user)
        address=Address.objects.filter(user__uname=user).order_by('id')
        return render(request, 'userprofile.html',{'profile':profile,'address':address})
    else:
        return redirect('userlogin')
    
class EditUserProfileView(View):
    def get(self, request):
        if 'uname' in request.session:
            user = request.session['uname']
            user = UserDetail.objects.get(uname=user)
            return render(request, 'edituserprofile.html', {'user': user})
        else:
            return redirect('userlogin')

    def post(self, request):
        if 'uname' in request.session:   
            user = request.session['uname']
            user = UserDetail.objects.get(uname=user)
            uemail = request.POST.get('uemail')
            uphone = request.POST.get('uphone')
            UserDetail.objects.filter(uname=user.uname).update(uemail=uemail, uphone=uphone)
            messages.success(request, 'User details updated successfully')
            return redirect('userprofile')
        else:
            return redirect('userlogin')
        
class ChangePasswordView(View):
    def get(self, request):
        if 'uname' in request.session:   
            return render(request,'changepassword.html')
        else:
            return redirect('userlogin')   
    def post(self, request):
        if 'uname' in request.session:
            user = request.session['uname']
            user = UserDetail.objects.get(uname=user)
            password = request.POST.get('upassword')
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')
            if user.upassword == password:
                if pass1 == pass2:
                    user.upassword = pass1
                    user.save()
                    messages.success(request, "Passwords changed successfully")
                    return redirect('userprofile')
                else:
                    messages.warning(request, "Passwords not matching")
            else:
                messages.warning(request, "Incorrect password")
            return redirect('changepassword')
        else:
            return redirect('userlogin')

def updateprofileaddress(request,id):
    if 'uname' in request.session:
        add = Address.objects.get(id=id)
        if request.method == 'POST':
            fm = UserAddressForm(request.POST, instance=add)
            if fm.is_valid():
                fm.save()
                messages.success(request,"Address updated successfully")
                return redirect('userprofile')
            else:
                return render(request, 'updateprofileaddress.html', {'fm': fm})
        else:
            fm = UserAddressForm(instance=add)
            return render(request, 'updateprofileaddress.html', {'fm': fm})
    else:
        return redirect('userlogin')
    
def addprofileaddress(request):
    if 'uname' in request.session:
        if request.method=='POST':
            fm = UserAddressForm(request.POST) 
            if fm.is_valid():
                use = request.session['uname']
                user = UserDetail.objects.get(uname = use)
                reg = fm.save(commit=False)
                reg.user = user
                reg.save()
                messages.success(request, 'new address added successfully')
                return redirect('userprofile') 
            else:
                return render(request, 'addprofileaddress.html', {'fm': fm})
        else:
            fm = UserAddressForm()
            return render(request, 'addprofileaddress.html', {'fm': fm})
    else:
        return redirect('userlogin')
    
def wishlist(request):
    if 'uname' in request.session:
        wish_id = request.GET.get('wish_id')
        if wish_id is not None:
            wish_product = Product.objects.get(id=wish_id)
            dup = Wishlist.objects.filter(product__name=wish_product.name).first()
            if dup is None:
                product = Product.objects.get(id=wish_id)
                use1 = request.session['uname']
                use2 = UserDetail.objects.get(uname=use1)
                wish = Wishlist(user=use2,product=product)
                wish.save()
                wish_items = Wishlist.objects.all().order_by('-id')
            else:
                messages.warning(request,'Item is already in the wishlist')
                wish_items = Wishlist.objects.all().order_by('-id')
        else:
            wish_items = Wishlist.objects.all().order_by('-id')
        return render(request,'wishlist.html',{'wish_items':wish_items})
    else:
        return redirect('userlogin')


def wishlistdelete(request,id):
    if 'uname' in request.session:
        Wishlist.objects.filter(id=id).delete()
        return redirect('wishlist')
    else:
        return redirect('userlogin')


# def sales_report(request):
#     if 'username' in request.session:
#         buf = io.BytesIO()
#         c = canvas.Canvas(buf,pagesize=letter, bottomup=1)
#         textob = c.beginText()
#         textob.setTextOrigin(inch, inch)
#         textob.setFont("Helvetica", 16)
#         if request.method == 'POST':    
#             start_date = request.POST.get('start_date')
#             end_date = request.POST.get('end_date')
#             orders = Order.objects.all()
#             if start_date and end_date:
#                 start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#                 end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#                 orders = orders.order_by('-ordered_date').filter(ordered_date__range=[start_date, end_date])
#             else:
#                 orders = Order.objects.all().order_by('-order_date')               
#             table_header = ["Customer Name", "Product Title", "Order Date and Time", "Order Status", "Payment Status"]            
#             table_data = []
#             for ord in orders:
#                 row_data = [ord.address.user.uname, ord.product.name, str(ord.ordered_date), str(ord.status), str(ord.ordertype)]
#                 table_data += [row_data]
#             pdfTable = Table([table_header] +table_data)           
#             pdfTableStyle = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue)]) 
#             pdfTable.setStyle(pdfTableStyle)
#             pdfTable.wrapOn(c, 100, 100)
#             pdfTable.drawOn(c, 10, 10 + 5)
#             c.drawText(textob)
#             c.showPage()
#             c.save()
#             buf.seek(0)
#             return FileResponse(buf, as_attachment=True, filename="Sales report.pdf")
#         else:
#             return render(request,'sales_report.html')
#     else:
#         return redirect('userlogin')
    
def cancelcoupon(request):
    uname = request.session['uname']
    Coupon.objects.filter(user__uname=uname).update(applied=False)
    messages.warning(request,'Coupon removed')
    return redirect('checkout')


def admincouponlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=Coupon.objects.filter(coupon_code__icontains=search)
        else:
            member=Coupon.objects.all().order_by('-id')
        return render(request,'admincouponlist.html',{'member': member})
    else:
        return render(request, 'adminlogin.html')
    
def adminaddcoupon(request):
    if 'username' in request.session:       
        if request.method == 'POST':
            fm = CouponForm(request.POST,request.FILES)
            if fm.is_valid():
                coupon_code = fm.cleaned_data['coupon_code']
                dup = Coupon.objects.filter(coupon_code=coupon_code).first()
                if dup:
                    messages.warning(request,'Coupon already exists')
                    return redirect('adminaddcoupon')
                else: 
                    fm.save()
                    return redirect('admincouponlist')       
        else:        
            fm = CouponForm()
            return render(request, 'adminaddcoupon.html',{'fm':fm})
    else:
        return render(request, 'adminlogin.html')

def deletecoupon(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Coupon.objects.filter(id=uid).delete()
        return redirect('admincouponlist')
    else:
        return redirect('adminlogin')

def updatecoupon(request):
    if 'username' in request.session:
        uid = request.GET['uid']
        cat = Coupon.objects.get(id=uid)
        if request.method == 'POST':
            fm = CouponForm(request.POST, request.FILES, instance=cat)
            if fm.is_valid():
                fm.save()
                return redirect('admincouponlist')
        else:
            fm = CouponForm(instance=cat)
            return render(request, 'adminupdatecoupon.html', {'fm': fm})
    else:
        return redirect('adminlogin')
    
def adminbannerlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=Banner.objects.filter(name__icontains=search)
        else:
            member=Banner.objects.all().order_by('-id')
        return render(request,'adminbannerlist.html',{'member': member})
    else:
        return render(request, 'adminlogin.html')
    
def updatebanner(request):
    if 'username' in request.session:
        uid = request.GET['uid']
        cat = Banner.objects.get(id=uid)
        if request.method == 'POST':
            fm = BannerForm(request.POST, request.FILES, instance=cat)
            if fm.is_valid():
                fm.save()
                return redirect('adminbannerlist')
        else:
            fm = BannerForm(instance=cat)
            return render(request, 'adminupdatebanner.html', {'fm': fm})
    else:
        return redirect('adminlogin')


def handle_not_found(request,exception):
    return render(request,'not-found.html')


def generateinvoice(request):
    user = UserDetail.objects.get(uname = request.session['uname'])

    ordered_product = Order.objects.get(Q(id=request.GET.get('ord_id')) & Q(user=user))  
    data = {
        # 'date' : datetime.date.today(),
        'orderid': ordered_product.id,
        'ordered_date': ordered_product.ordered_date,
        'name': ordered_product.address.name,
        'housename': ordered_product.address.housename,
        'locality' : ordered_product.address.locality,
        'city' : ordered_product.address.city, 
        'state' : ordered_product.address.state, 
        'zipcode': ordered_product.address.zipcode,
        'phone' : ordered_product.address.phone,
        'product': ordered_product.product.name,
        'amount' : ordered_product.amount,
        'ordertype': ordered_product.ordertype,
    } 
    print("DATAAAA",data)
    template_path = 'invoicepdf.html'
    context = {
        # 'date': data['date'],
        'orderid': data['orderid'],
        'name': data['name'],
    }
    html = render_to_string(template_path, data)
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{data["orderid"]}.pdf"'
  

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import requests
from django.template.loader import get_template
import openpyxl
import pytz
from datetime import datetime
from django.db import models
from django.db.models import Sum
from io import BytesIO

def sales_report(request):
    if 'username' in request.session:
        if request.method == 'POST':    
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            generate = request.POST.get('generate')
            order = Order.objects.all()
            print(generate)
            print(start_date)
            if end_date < start_date:
                messages.warning(request, 'invalid date')
                return redirect('admindashboard')

            if generate == 'PDF':
                if start_date and end_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    total_ordered_products = Order.objects.filter(ordered_date__range=[start_date, end_date])
                return redirect('admindashboard')

        else:
            return render(request,'sales_report.html')
    else:
        return redirect('userlogin')

