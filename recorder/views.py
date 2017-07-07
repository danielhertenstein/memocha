from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'recorder/index.html')


@login_required
def user(request):
    return render(request, 'recorder/user.html')
