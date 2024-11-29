from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django import forms
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    
    address = forms.CharField(max_length=255, required=False, label='Adress')
    phone = forms.CharField(max_length=15, required=False, label='phone')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2','address','phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        if len(phone) != 8:
            raise ValidationError("Le numéro de téléphone doit contenir exactement 8 chiffres.")
        if phone[0] not in ['3', '4', '5']:
            raise ValidationError("Entrer un numero de telephone valide")    
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email    


   