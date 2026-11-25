from django.urls import path
from . import views

urlpatterns = [
    path('', views.domov, name='domov'),
]
