import json
from datetime import datetime, timedelta
from collections import defaultdict
from functools import partial

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory, modelformset_factory
from django.core.serializers.json import DjangoJSONEncoder

from recorder.forms import MyUserCreationForm, PatientCreationForm, PrescriptionForm, PatientAccountForm, UploadFileForm
from recorder.models import Doctor, Patient, Prescription, Video


def index(request):
    return render(request, 'recorder/index.html')


@login_required
def patient_dashboard(request):
    patient = Patient.objects.get(user=request.user)

    recordable_meds, recordable_med_times = patient.recordable_medications()
    recordable_med_times = [time.strftime('%H:%M') for time in recordable_med_times]

    next_meds, next_med_time = patient.next_medication()
    next_med_time = next_med_time.strftime('%H:%M')

    video_dict = defaultdict(partial(defaultdict, partial(defaultdict, dict)))
    dates_of_interest = [(datetime.today() - timedelta(days=i)).date() for i in [4, 3, 2, 1, 0]]
    for date in dates_of_interest:
        videos = patient.videos_for_date(date)
        for video in videos:
            dosage_details = video.corresponding_dosage()
            video_dict[dosage_details['date']][dosage_details['medication']][dosage_details['timeslot']] = dosage_details['url']
    video_dict_json = json.dumps(video_dict)

    prescriptions = list(patient.prescriptions.all().values_list())
    prescriptions_json = json.dumps(prescriptions, cls=DjangoJSONEncoder)
    return render(
        request,
        'recorder/patient_dashboard.html',
        {
            'patient': patient,
            'next_meds': next_meds,
            'next_med_time': next_med_time,
            'recordable_meds': recordable_meds,
            'recordable_med_times': recordable_med_times,
            'dates_of_interest': [date.strftime('%d %b') for date in dates_of_interest],
            'prescriptions': prescriptions_json,
            'video_dict': video_dict_json,
        }
    )


@login_required
def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    patients = doctor.patient_set.all()
    return render(request, 'recorder/doctor_dashboard.html', {'patients': patients})


def patient_creation(request):
    if request.method == 'POST':
        form = PatientAccountForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            username = '{0}_{1}_{2}'.format(first_name, last_name, date_of_birth)
            secure_code = form.cleaned_data.get('secure_code')

            implied_user = User.objects.filter(username=username)
            if not implied_user:
                same_name_users = User.objects.filter(
                    first_name=first_name,
                    last_name=last_name,
                )
                for user in same_name_users:
                    if user.patient.date_of_birth == date_of_birth:
                        message = ('An account with this name and date of '
                                   'birth has already been activated. Return '
                                   'to the home screen and log in.')
                        form.add_error('__all__', message)
                    break
                else:
                    message = ('No matching patient record has been registered '
                               'by a doctor. Please contact your doctor to '
                               'ensure your record has been created.')
                    form.add_error('__all__', message)

            if not form.errors:
                user = authenticate(
                    username=username,
                    password=secure_code
                )
                if user is None:
                    message = ('The name, date of birth, and secure code '
                               'entered do not match those provided by your '
                               'doctor. Please try again.')
                    form.add_error('__all__', message)
                else:
                    # Update user account
                    user.username = form.cleaned_data.get('username')
                    user.set_password(form.cleaned_data.get('password1'))
                    user.save()

                    login(request, user)
                    return redirect('/recorder/patient')
    else:
        form = PatientAccountForm()
    return render(request, 'recorder/patient_creation.html', {'form': form})


def doctor_creation(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Doctors')
            user.groups.add(group)
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
            group = Group.objects.get(name='Patients')
            user.groups.add(group)
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
        # A set to keep track of which previously existing prescriptions are in
        # the new formset.
        existing_prescriptions = set([prescription.pk for prescription in patient.prescriptions.all()])
        formset = formset_factory(PrescriptionForm)(request.POST, prefix='p_form')
        if formset.is_valid():
            for form in formset:
                # Check to see if the form matches an existing prescription.
                matching_prescriptions = patient.prescriptions.filter(
                    medication=form.cleaned_data['medication'],
                    dosage=form.cleaned_data['dosage'],
                    dosage_times=form.cleaned_data['dosage_times']
                )
                if matching_prescriptions:
                    # Remove the matching prescription from the tracker.
                    for prescription in matching_prescriptions:
                        existing_prescriptions.remove(prescription.pk)
                    # Don't need to add this one because it already exists.
                    continue
                # Add the new prescription.
                prescription = form.save()
                patient.prescriptions.add(prescription)
            # Any keys left in the existing_prescriptions set were not present
            # in the formset and we can assume they have been removed.
            for prescription in existing_prescriptions:
                patient.prescriptions.get(pk=prescription).delete()
            return redirect('/recorder/doctor')
    else:
        if patient.prescriptions.all():
            formset = modelformset_factory(Prescription, fields='__all__', extra=0)(prefix='p_form', queryset=patient.prescriptions.all())
        else:
            formset = modelformset_factory(Prescription, fields='__all__')(prefix='p_form')
    return render(request, 'recorder/patient_details.html', {'patient': patient, 'formset': formset})


@login_required
def record_video(request):

    if request.method == 'GET':
        return redirect('/recorder/patient')
    medication = request.POST['medication']
    form = UploadFileForm(request.POST, request.FILES, initial={'medication': medication})
    if form.is_valid() and request.FILES:
        patient = Patient.objects.get(user=request.user)
        video = Video(
            person=patient,
            record_date=datetime.now(),
            prescription=patient.prescriptions.get(medication=medication),
            upload=request.FILES['data']
        )
        video.save()
        # No need to redirect here since the AJAX request in video.js does it
        # for us. The AJAX request will redirect to the patient dashboard.
    return render(request, 'recorder/record_video.html', {'form': form})
