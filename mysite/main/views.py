from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'home.html')

def v1(response):
    return HttpResponse("<h1>View 1</h1>")
