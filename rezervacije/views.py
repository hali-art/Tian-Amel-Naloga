from django.shortcuts import render


def domov(request):
    return render(request, 'rezervacije/domov.html')
