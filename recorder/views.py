from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from recorder.forms import MyUserCreationForm
from recorder.models import Doctor


def index(request):
    return render(request, 'recorder/index.html')


@login_required
def patient_dashboard(request):
    return render(request, 'recorder/patient_dashboard.html')

@login_required
def doctor_dashboard(request):
    return render(request, 'recorder/doctor_dashboard.html')


def patient_creation(request):
    return render(request, 'recorder/patient_creation.html')


def doctor_creation(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            doctor = Doctor.objects.create(user=user)
            user = authenticate(
                username=doctor.user.username,
                password=form.cleaned_data.get('password1')
            )
            login(request, user)
            return redirect('/recorder/doctor')
    else:
        form = MyUserCreationForm()
    return render(request, 'recorder/doctor_creation.html', {'form': form})
