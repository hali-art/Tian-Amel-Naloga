from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistracijaForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Ime', max_length=50)
    last_name = forms.CharField(label='Priimek', max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
