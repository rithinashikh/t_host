from django import forms
from phase.models import Product, Coupon, Banner
from django.forms import ModelForm
import re
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = ['name', 'normalprice','description','image','stock','category']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'normalprice' : forms.TextInput(attrs={'class':'form-control'}),
            'description' : forms.Textarea(attrs={'class':'form-control','rows': 4}),         
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'category' : forms.Select(attrs={'class':'form-control'}),

        }
        labels={
            'name':'Product Name',
            'normalprice':'Price',
            'description':'Description',
            'stock':'Stock',
            'category':'Category'
        }
    def clean_normalprice(self):
        normalprice = self.cleaned_data['normalprice']
        if not re.match(r'^\d+(\.\d{1,2})?$', str(normalprice)):
            raise ValidationError("Price must be a number with up to 2 decimal places.")
        return normalprice

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise ValidationError("Stock must be a non-negative integer.")
        return stock


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['coupon_code', 'is_active', 'discount_price', 'minimum_amount', 'user']
        labels = {
            'coupon_code': 'Coupon Code',
            'is_active': 'Is Active',
            'discount_price': 'Discount Price',
            'minimum_amount': 'Minimum Amount',
            'user': 'User',
        }
        widgets = {
            'coupon_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }



class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['name', 'image']
        labels = {
            'name': 'Banner name',
            # 'image': 'Image',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'image': forms.FileInput(attrs={'class':'form-control'}),
        }