from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html')

def content(request):
    return render(request, 'main/content.html')

def grades(request):
    return render(request, 'main/grades.html')

def index(request):
    return render(request, 'main/index.html')

def quiz(request):
    return render(request, 'main/quiz.html')

def practice(request):
    return render(request, 'main/practice.html')

def home(request):
    return render(request, 'main/home.html')
