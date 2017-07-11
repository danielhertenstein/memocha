from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory

from recorder.forms import MyUserCreationForm, PatientCreationForm, PrescriptionForm
from recorder.models import Doctor, Patient, Prescription


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


@login_required
def add_patient(request):
    if request.method == 'POST':
        form = PatientCreationForm(request.POST)
        formset = formset_factory(PrescriptionForm)(request.POST, prefix='p_form')
        if form.is_valid() and formset.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            username = '{0}_{1}_{2}'.format(first_name, last_name, date_of_birth)
            password = make_password(form.cleaned_data.get('secure_code'))
            email = form.cleaned_data.get('email')
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password,
                email=email,
            )
            patient = Patient.objects.create(
                user=user,
                doctor=request.user.doctor,
                date_of_birth=date_of_birth,
            )
            for sub_form in formset:
                prescription = sub_form.save()
                patient.prescriptions.add(prescription)
            return redirect('/recorder/doctor')
    else:
        form = PatientCreationForm()
        formset = formset_factory(PrescriptionForm)(prefix='p_form')
    return render(request, 'recorder/add_patient.html', {'form': form, 'formset': formset})


@login_required
def patient_details(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        formset = formset_factory(PrescriptionForm)(request.POST, prefix='p_form')
        if formset.is_valid():
            # TODO: Where to redirect to?
            return redirect('/recorder/doctor')
    else:
        # TODO: Fill formset with prescriptions
        formset = formset_factory(PrescriptionForm)(prefix='p_form')
    return render(request, 'recorder/patient_details.html', {'patient': patient, 'formset': formset})