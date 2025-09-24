from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'main/index.html')

@login_required
def home(request):
    return render(request, 'main/home.html')

@login_required
def content(request):
    return render(request, 'main/content.html')

@login_required
def grades(request):
    return render(request, 'main/grades.html')

@login_required
def practice(request):
    return render(request, 'main/practice.html')



