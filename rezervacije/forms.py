from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegistracijaForm(UserCreationForm):
    email = forms.EmailField(label='E-pošta', required=True)
    first_name = forms.CharField(label='Ime', max_length=50)
    last_name = forms.CharField(label='Priimek', max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        namigi = {
            'username': 'npr. ana123',
            'first_name': 'Ana',
            'last_name': 'Novak',
            'email': 'ana@primer.si',
        }
        for ime, namig in namigi.items():
            self.fields[ime].widget.attrs['placeholder'] = namig
        self.fields['username'].widget.attrs['autofocus'] = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Uporabnik s tem e-poštnim naslovom že obstaja.')
        return email


class PrijavaForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Uporabniško ime'
        self.fields['password'].widget.attrs['placeholder'] = 'Geslo'
