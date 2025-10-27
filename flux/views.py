from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, "flux/index.html")

def cart(request):
    return render(request, "flux/cart.html")


def cheackout(request):
    return render(request, "flux/cheackout.html")