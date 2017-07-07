from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'recorder/index.html')


@login_required
def patient_dashboard(request):
    return render(request, 'recorder/patient_dashboard.html')

@login_required
def doctor_dashboard(request):
    return render(request, 'recorder/doctor_dashboard.html')
