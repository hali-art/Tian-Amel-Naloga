from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegistracijaForm, PrijavaForm
from .models import Storitev, Frizer, Rezervacija


def domov(request):
    # na domači strani pokažemo nekaj storitev in frizerje
    storitve = Storitev.objects.all().order_by('cena')[:3]
    frizerji = Frizer.objects.all().order_by('ime')
    return render(request, 'rezervacije/domov.html', {
        'storitve': storitve,
        'frizerji': frizerji,
    })


def seznam_storitev(request):
    storitve = Storitev.objects.all().order_by('ime')
    return render(request, 'rezervacije/storitve.html', {'storitve': storitve})


def preveri_datum(datum):
    """Vrne napako, če datuma ni mogoče izbrati, sicer None."""
    if datum < timezone.localdate():
        return 'Ne morete izbrati datuma v preteklosti.'
    if datum.weekday() == 6:
        return 'Ob nedeljah je salon zaprt.'
    return None


def prosti_termini(frizer, storitev, datum):
    """Vrne seznam ur (time), ko je frizer prost za izbrano storitev."""
    if preveri_datum(datum):
        return []

    korak = timedelta(minutes=30)
    trajanje = timedelta(minutes=storitev.trajanje)

    zacetek = datetime.combine(datum, frizer.zacetek_dela)
    konec = datetime.combine(datum, frizer.konec_dela)

    # že zasedeni termini tega frizerja na ta dan
    zasedeni = []
    rezervacije = Rezervacija.objects.filter(frizer=frizer, datum=datum, status='potrjena')
    for r in rezervacije:
        z = datetime.combine(datum, r.ura)
        zasedeni.append((z, z + timedelta(minutes=r.storitev.trajanje)))

    termini = []
    cas = zacetek
    # lokalni čas (Ljubljana), brez časovnega pasu, da ga lahko primerjamo
    zdaj = timezone.localtime().replace(tzinfo=None)
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
    frizerji = Frizer.objects.all().order_by('ime')

    izbran_frizer = None
    izbran_datum = None
    termini = None
    napaka = None

    frizer_id = request.GET.get('frizer')
    datum_str = request.GET.get('datum')

    if frizer_id and datum_str:
        izbran_frizer = frizerji.filter(id=frizer_id).first() if frizer_id.isdigit() else None
        try:
            izbran_datum = datetime.strptime(datum_str, '%Y-%m-%d').date()
        except ValueError:
            napaka = 'Datum ni pravilen.'

        if izbran_frizer is None:
            napaka = 'Izbrani frizer ne obstaja.'
        elif izbran_datum:
            napaka = preveri_datum(izbran_datum)
            if napaka is None:
                termini = prosti_termini(izbran_frizer, storitev, izbran_datum)

    return render(request, 'rezervacije/izbira_termina.html', {
        'storitev': storitev,
        'frizerji': frizerji,
        'izbran_frizer': izbran_frizer,
        'izbran_datum': izbran_datum,
        'termini': termini,
        'napaka': napaka,
        'danes': timezone.localdate(),
    })


@login_required(login_url='prijava')
def rezerviraj(request):
    # podatki pridejo iz izbire termina (GET) oz. iz obrazca (POST)
    podatki = request.POST if request.method == 'POST' else request.GET
    try:
        storitev = Storitev.objects.get(id=podatki.get('storitev'))
        frizer = Frizer.objects.get(id=podatki.get('frizer'))
        datum = datetime.strptime(podatki.get('datum'), '%Y-%m-%d').date()
        ura = datetime.strptime(podatki.get('ura'), '%H:%M').time()
    except (Storitev.DoesNotExist, Frizer.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Napačni podatki za rezervacijo.')
        return redirect('storitve')

    if request.method == 'POST':
        # še enkrat preverimo, ali je termin res še prost (da ga ni kdo vmes zasedel)
        if ura not in prosti_termini(frizer, storitev, datum):
            messages.error(request, 'Ta termin je žal že zaseden. Izberite drugega.')
            # vrnemo ga na isti dan in istega frizerja, da mu ni treba vsega izbirati znova
            url = reverse('izbira_termina', args=[storitev.id])
            return redirect(f'{url}?frizer={frizer.id}&datum={datum:%Y-%m-%d}')

        rezervacija = Rezervacija.objects.create(
            uporabnik=request.user,
            frizer=frizer,
            storitev=storitev,
            datum=datum,
            ura=ura,
        )
        return redirect('potrditev', rezervacija_id=rezervacija.id)

    return render(request, 'rezervacije/rezerviraj.html', {
        'storitev': storitev,
        'frizer': frizer,
        'datum': datum,
        'ura': ura,
    })


@login_required(login_url='prijava')
def potrditev(request, rezervacija_id):
    rezervacija = get_object_or_404(Rezervacija, id=rezervacija_id, uporabnik=request.user)
    return render(request, 'rezervacije/potrditev.html', {'rezervacija': rezervacija})


@login_required(login_url='prijava')
def moje_rezervacije(request):
    zdaj = timezone.localtime()
    rezervacije = Rezervacija.objects.filter(uporabnik=request.user)
    # prihajajoče so tiste od jutri naprej in današnje, ki se še niso začele
    se_niso_bile = Q(datum__gt=zdaj.date()) | Q(datum=zdaj.date(), ura__gt=zdaj.time())
    prihajajoce = rezervacije.filter(se_niso_bile, status='potrjena').order_by('datum', 'ura')
    pretekle = rezervacije.exclude(id__in=prihajajoce).order_by('-datum', '-ura')
    return render(request, 'rezervacije/moje_rezervacije.html', {
        'prihajajoce': prihajajoce,
        'pretekle': pretekle,
    })


@login_required(login_url='prijava')
def preklici_rezervacijo(request, rezervacija_id):
    rezervacija = get_object_or_404(Rezervacija, id=rezervacija_id, uporabnik=request.user)
    if request.method == 'POST':
        zdaj = timezone.localtime().replace(tzinfo=None)
        if datetime.combine(rezervacija.datum, rezervacija.ura) <= zdaj:
            messages.error(request, 'Pretekle rezervacije ni mogoče preklicati.')
        elif rezervacija.status == 'preklicana':
            messages.info(request, 'Ta rezervacija je že preklicana.')
        else:
            rezervacija.status = 'preklicana'
            rezervacija.save()
            messages.success(request, 'Rezervacija je preklicana.')
    return redirect('moje_rezervacije')


@login_required(login_url='prijava')
def pregled_frizer(request):
    # do strani lahko pride samo frizer (uporabnik, ki je povezan s frizerjem)
    frizer = Frizer.objects.filter(uporabnik=request.user).first()
    if frizer is None:
        messages.error(request, 'Do te strani imajo dostop samo frizerji.')
        return redirect('domov')

    datum = timezone.localdate()
    datum_str = request.GET.get('datum')
    if datum_str:
        try:
            datum = datetime.strptime(datum_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    rezervacije = Rezervacija.objects.filter(
        frizer=frizer, datum=datum, status='potrjena'
    ).order_by('ura')

    return render(request, 'rezervacije/pregled_frizer.html', {
        'frizer': frizer,
        'datum': datum,
        'prejsnji': datum - timedelta(days=1),
        'naslednji': datum + timedelta(days=1),
        'rezervacije': rezervacije,
    })


def registracija(request):
    if request.user.is_authenticated:
        return redirect('domov')

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
    if request.user.is_authenticated:
        return redirect('domov')

    if request.method == 'POST':
        form = PrijavaForm(request, data=request.POST)
        if form.is_valid():
            uporabnik = form.get_user()
            login(request, uporabnik)
            messages.success(request, f'Pozdravljeni, {uporabnik.first_name or uporabnik.username}!')
            # če je prišel s strani, ki zahteva prijavo, ga vrnemo nazaj
            # (samo na naš strežnik, ne na kakšno tujo stran)
            naslednja = request.GET.get('next')
            if naslednja and url_has_allowed_host_and_scheme(naslednja, allowed_hosts={request.get_host()}):
                return redirect(naslednja)
            return redirect('domov')
    else:
        form = PrijavaForm()
    return render(request, 'rezervacije/prijava.html', {'form': form})


def odjava(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Uspešno ste se odjavili.')
    return redirect('domov')
