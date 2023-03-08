from django import forms
from phase.models import Category
from django.forms import ModelForm

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'offer_active', 'discount']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'offer_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels={
            'name':'Category Name',
            'offer_active': 'Offer Active',
            'discount': 'Discount Price',
        }

