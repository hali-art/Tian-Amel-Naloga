from django.urls import path
from . import views

urlpatterns = [
    path('', views.domov, name='domov'),
    path('storitve/', views.seznam_storitev, name='storitve'),
    path('storitve/<int:storitev_id>/termin/', views.izbira_termina, name='izbira_termina'),
    path('rezerviraj/', views.rezerviraj, name='rezerviraj'),
    path('rezervacija/<int:rezervacija_id>/potrditev/', views.potrditev, name='potrditev'),
    path('registracija/', views.registracija, name='registracija'),
    path('prijava/', views.prijava, name='prijava'),
    path('odjava/', views.odjava, name='odjava'),
]
