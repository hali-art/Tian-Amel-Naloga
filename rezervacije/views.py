from datetime import datetime, timedelta, date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .forms import RegistracijaForm
from .models import Storitev, Frizer, Rezervacija


def domov(request):
    return render(request, 'rezervacije/domov.html')


def seznam_storitev(request):
    storitve = Storitev.objects.all().order_by('ime')
    return render(request, 'rezervacije/storitve.html', {'storitve': storitve})


def prosti_termini(frizer, storitev, datum):
    """Vrne seznam ur (time) ko je frizer prost za izbrano storitev."""
    korak = timedelta(minutes=30)
    trajanje = timedelta(minutes=storitev.trajanje)

    zacetek = datetime.combine(datum, frizer.zacetek_dela)
    konec = datetime.combine(datum, frizer.konec_dela)

    # ze zasedeni termini tega frizerja na ta dan
    zasedeni = []
    rezervacije = Rezervacija.objects.filter(frizer=frizer, datum=datum, status='potrjena')
    for r in rezervacije:
        z = datetime.combine(datum, r.ura)
        zasedeni.append((z, z + timedelta(minutes=r.storitev.trajanje)))

    termini = []
    cas = zacetek
    zdaj = datetime.now()
    while cas + trajanje <= konec:
        prost = True
        for z, k in zasedeni:
            # termina se prekrivata
            if cas < k and cas + trajanje > z:
                prost = False
                break
        if cas <= zdaj:
            prost = False
        if prost:
            termini.append(cas.time())
        cas += korak
    return termini


def izbira_termina(request, storitev_id):
    storitev = get_object_or_404(Storitev, id=storitev_id)
    frizerji = Frizer.objects.all()

    izbran_frizer = None
    izbran_datum = None
    termini = None
    napaka = None

    frizer_id = request.GET.get('frizer')
    datum_str = request.GET.get('datum')

    if frizer_id and datum_str:
        izbran_frizer = get_object_or_404(Frizer, id=frizer_id)
        try:
            izbran_datum = datetime.strptime(datum_str, '%Y-%m-%d').date()
        except ValueError:
            napaka = 'Datum ni pravilen.'

        if izbran_datum:
            if izbran_datum < date.today():
                napaka = 'Ne morete izbrati datuma v preteklosti.'
            elif izbran_datum.weekday() == 6:
                napaka = 'Ob nedeljah je salon zaprt.'
            else:
                termini = prosti_termini(izbran_frizer, storitev, izbran_datum)

    return render(request, 'rezervacije/izbira_termina.html', {
        'storitev': storitev,
        'frizerji': frizerji,
        'izbran_frizer': izbran_frizer,
        'izbran_datum': izbran_datum,
        'termini': termini,
        'napaka': napaka,
        'danes': date.today(),
    })


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
