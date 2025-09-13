from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'main/index.html')

def signup(request):
    return render(request, 'signup.html')

def content(request):
    return render(request, 'content.html')

def grades(request):
    return render(request, 'grades.html')

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def quiz(request):
    return render(request, 'quiz.html')

def practice(request):
    return render(request, 'practice.html')

def home(request):
    return render(request, 'main/home.html')
