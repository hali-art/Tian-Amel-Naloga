from django.urls import path
from . import views

urlpatterns = [
    path('', views.domov, name='domov'),
    path('registracija/', views.registracija, name='registracija'),
    path('prijava/', views.prijava, name='prijava'),
    path('odjava/', views.odjava, name='odjava'),
]
