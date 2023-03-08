from django import forms
from phase.models import UserDetail, Address, Order
from django.forms import ModelForm
import re
from django.core.exceptions import ValidationError

class UserSignupForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['uname', 'uemail','uphone','upassword', 'uimage']
        widgets = {
            'uname' : forms.TextInput(attrs={'class':'form-control'}),
            'uemail' : forms.EmailInput(attrs={'class':'form-control'}),
            'uphone' : forms.NumberInput(attrs={'class':'form-control'}),
            'upassword' : forms.PasswordInput(attrs={'class':'form-control'}),
            'uimage' : forms.FileInput(attrs={'class':'form-control'}),
        }
        labels={
            'uname':'User Name',
            'uemail':'Email',
            'uphone':'Phone no',
            'upassword':'Password',
            'uimage':'Image',
        }
    def clean_uphone(self):
        uphone = self.cleaned_data['uphone']
        if UserDetail.objects.filter(uphone=uphone).exists():
            raise ValidationError("This Phone number already exists.")
        if not re.match(r'^\d{10}$', uphone):
            raise ValidationError("Phone number must be 10 digit")
        return uphone
    def clean_uname(self):
        uname = self.cleaned_data['uname']
        if UserDetail.objects.filter(uname=uname).exists():
            raise ValidationError("This user already exists.")
        if not re.match(r'^[A-Za-z]{4,8}$', uname):
            raise ValidationError("Length of username must be between 4 to 8")
        return uname

    def clean_uemail(self):
        uemail = self.cleaned_data['uemail']
        if UserDetail.objects.filter(uemail=uemail).exists():
            raise ValidationError("This email is already registered.")
        # if not re.match(r'^[A-Za-z]{2,4}$+@[A-Za-z]{2,4}+.[A-Za-z]{2,4}$', uemail):
        #     raise ValidationError("Invalid email address")
        return uemail
    
    def clean_upassword(self):
        upassword = self.cleaned_data['upassword']
        if not re.match(r'^[A-Za-z]{4,8}$', upassword):
            raise ValidationError("Length of password must be between 4 to 8")
        return upassword




class UserLoginForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['uname','upassword']
        widgets = {
            'uname' : forms.TextInput(attrs={'class':'form-control'}),
            'upassword' : forms.PasswordInput(attrs={'class':'form-control'}),
        }
        labels={
            'uname':'User Name',
            'upassword':'Password',
        }

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["name","housename", "locality", "phone", "city", "state", "zipcode"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'housename': forms.TextInput(attrs={'class': 'form-control'}),
            "locality": forms.TextInput(attrs={'class': 'form-control'}),
            "city": forms.TextInput(attrs={'class': 'form-control'}),
            "state": forms.Select(attrs={'class': 'form-control'}),
            "zipcode": forms.NumberInput(attrs={'class': 'form-control'}),
            "phone": forms.TextInput(attrs={'class': 'form-control'}),

        }
        labels={
            'name':'Name',
            'housename':'House no.',
            'locality':'Locality',
            'city':'City',
            'state':'State',
            'zipcode':'Zipcode',
            'phone':'Phone',
        }
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be entered in the format: '9999999999'")
        return phone

    def clean_zipcode(self):
        zipcode = self.cleaned_data['zipcode']
        if not re.match(r'^\d{6}$', str(zipcode)):
            raise ValidationError("Zip code must be 6 digits.")
        return zipcode


        
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordertype','status']
        widgets = {
            'ordertype' : forms.TextInput(attrs={'class':'form-control'}),
            'status' : forms.Select(attrs={'class':'form-control'}),
        }
        labels={
            'ordertype':'Order Type',
            'status':'Status',
        }
