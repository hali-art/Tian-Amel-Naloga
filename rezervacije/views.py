from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .forms import RegistracijaForm


def domov(request):
    return render(request, 'rezervacije/domov.html')


def registracija(request):
    if request.method == 'POST':
        form = RegistracijaForm(request.POST)
        if form.is_valid():
            uporabnik = form.save()
            login(request, uporabnik)
            messages.success(request, 'Registracija je bila uspešna!')
            return redirect('domov')
    else:
        form = RegistracijaForm()
    return render(request, 'rezervacije/registracija.html', {'form': form})


def prijava(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # ce je prisel iz strani ki rabi prijavo ga vrnemo nazaj
            naslednja = request.GET.get('next')
            if naslednja:
                return redirect(naslednja)
            return redirect('domov')
    else:
        form = AuthenticationForm()
    return render(request, 'rezervacije/prijava.html', {'form': form})


def odjava(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Uspešno ste se odjavili.')
    return redirect('domov')
