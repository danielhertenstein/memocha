from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, world.")


@login_required
def user(request):
    return render(request, 'recorder/user.html')
