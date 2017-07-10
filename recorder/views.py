from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.forms import formset_factory

from recorder.forms import MyUserCreationForm, PatientCreationForm, PrescriptionForm
from recorder.models import Doctor


def index(request):
    return render(request, 'recorder/index.html')


@login_required
def patient_dashboard(request):
    return render(request, 'recorder/patient_dashboard.html')

@login_required
def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    patients = doctor.patient_set.all()
    return render(request, 'recorder/doctor_dashboard.html', {'patients': patients})


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


def add_patient(request):
    if request.method == 'POST':
        form = PatientCreationForm(request.POST)
        formset = formset_factory(PrescriptionForm)(request.POST, prefix='p_form')
        if form.is_valid() and formset.is_valid():
            print('boo')
            return redirect('/recorder/doctor')
    else:
        form = PatientCreationForm()
        formset = formset_factory(PrescriptionForm)(prefix='p_form')
    return render(request, 'recorder/add_patient.html', {'form': form, 'formset': formset})