# Tian-Amel-Naloga
Aplikacija za naročanje na frizerske storitve, kjer si lahko uporabnik izbere želeni termin in vrsto frizure, ki jo želi. Sistem bo omogočal enostavno in pregledno rezervacijo termina pri frizerju.

## Ekipa
- **Tian** – pogledi (views) in kontrolerji
- **Aleksander** – podatkovna baza in modeli (Django)
- **Amel** – testiranje in dokumentacija

## Zagon projekta

1. Kloniraj repozitorij in pojdi v mapo projekta:
   ```
   git clone https://github.com/hali-art/Tian-Amel-Naloga.git
   cd Tian-Amel-Naloga
   ```
2. Ustvari in aktiviraj virtualno okolje:
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Linux / macOS)
   ```
3. Namesti knjižnice:
   ```
   pip install -r requirements.txt
   ```
4. Ustvari bazo in zaženi strežnik:
   ```
   python manage.py migrate
   python manage.py runserver
   ```
5. Aplikacija je dostopna na http://127.0.0.1:8000/
