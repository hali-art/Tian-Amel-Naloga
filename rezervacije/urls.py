from django.urls import path
from . import views

urlpatterns = [
    path('', views.domov, name='domov'),
    path('storitve/', views.seznam_storitev, name='storitve'),
    path('registracija/', views.registracija, name='registracija'),
    path('prijava/', views.prijava, name='prijava'),
    path('odjava/', views.odjava, name='odjava'),
]
