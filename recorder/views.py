from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def index(request):
    return HttpResponse("Hello, world.")


@login_required
def user(request):
    return HttpResponse("User page.")