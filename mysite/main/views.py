from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'home.html')

def signup(request):
    return render(request, 'signup.html')
