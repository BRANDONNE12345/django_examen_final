from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    # Ajout des champs que vous utilisez dans le template
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

class CustomProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre prénom"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre nom"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Votre email"}),
        }
