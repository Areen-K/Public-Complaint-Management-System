from django import forms
from django.contrib.auth.models import User
from .models import Complaint
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'other_category', 'location', 'description', 'before_image']
        labels = {
            'other_category': 'Specify Category',
            'location': 'Area / Locality',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'other_category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'id': 'otherCategoryInput'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter area or ward name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'before_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
