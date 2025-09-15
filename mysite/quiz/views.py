from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def choose(request):
    return HttpResponse("Quiz home OK (replace with template later).")

@login_required
def take_quiz(request):
    return HttpResponse("Take quiz OK (replace with template later).")

