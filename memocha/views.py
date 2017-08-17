import json
from datetime import datetime, timedelta

from django.db.models import Count
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory, modelformset_factory
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from memocha.forms import MyUserCreationForm, PatientCreationForm, PrescriptionForm, PatientAccountForm, UploadFileForm
from memocha.models import Doctor, Patient, Prescription, Video


def index(request):
    return render(request, 'memocha/index.html')


@login_required
def dashboard(request):
    if request.user.groups.filter(name='Patients').exists():
        return redirect('/memocha/patient')
    else:
        return redirect('/memocha/doctor')


@login_required
def patient_dashboard(request):
    if not request.user.groups.filter(name='Patients').exists():
        return redirect('/accounts/login?next={0}'.format(request.path))
    patient = Patient.objects.get(user=request.user)

    recordable_meds, recordable_med_times = patient.recordable_medications()
    recordable_med_times = [time.strftime('%H:%M') for time in recordable_med_times]

    next_meds, next_med_time = patient.next_medication()
    next_med_time = next_med_time.strftime('%H:%M')

    dates_of_interest = [datetime.today() - timedelta(days=i)
                         for i in [4, 3, 2, 1, 0]]

    video_list = []
    videos = patient.video_set.filter(record_date__range=(
        dates_of_interest[0].date(), dates_of_interest[-1]
    ))
    for video in videos:
        video_list.append(video.corresponding_dosage())
    video_list_json = json.dumps(video_list)

    prescriptions = list(patient.prescriptions.all().values_list())
    prescriptions_json = json.dumps(prescriptions, cls=DjangoJSONEncoder)
    return render(
        request,
        'memocha/patient_dashboard.html',
        {
            'patient': patient,
            'next_meds': next_meds,
            'next_med_time': next_med_time,
            'recordable_meds': recordable_meds,
            'recordable_med_times': recordable_med_times,
            'dates_of_interest': [date.strftime('%d %b') for date in dates_of_interest],
            'prescriptions': prescriptions_json,
            'video_list': video_list_json,
        }
    )


@login_required
def doctor_dashboard(request):
    if not request.user.groups.filter(name='Doctors').exists():
        return redirect('/accounts/login?next={0}'.format(request.path))
    doctor = Doctor.objects.get(user=request.user)
    patients = doctor.patient_set.all()
    return render(request, 'memocha/doctor_dashboard.html', {'patients': patients})


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
                existing_user = User.objects.filter(
                    first_name=first_name,
                    last_name=last_name,
                    patient__date_of_birth=date_of_birth
                )
                if existing_user:
                    message = ('An account with this name and date of '
                               'birth has already been activated. Return '
                               'to the home screen and log in.')
                    form.add_error('__all__', message)
                else:
                    message = ('No matching patient record has been registered '
                               'by a doctor. Please check the name and date of '
                               'birth entered or contact your doctor to ensure '
                               'your record has been created.')
                    form.add_error('__all__', message)

            if not form.errors:
                user = authenticate(
                    username=username,
                    password=secure_code
                )
                if user is None:
                    message = ('The secure code entered do not match that '
                               'provided by your doctor. Please try again.')
                    form.add_error('__all__', message)
                else:
                    # Update user account
                    user.username = form.cleaned_data.get('username')
                    user.set_password(form.cleaned_data.get('password1'))
                    user.save()

                    login(request, user)
                    return redirect('/memocha/patient')
    else:
        form = PatientAccountForm()
    return render(request, 'memocha/patient_creation.html', {'form': form})


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
            return redirect('/memocha/doctor')
    else:
        form = MyUserCreationForm()
    return render(request, 'memocha/doctor_creation.html', {'form': form})


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
            return redirect('/memocha/doctor')
    else:
        form = PatientCreationForm()
        formset = formset_factory(PrescriptionForm)(prefix='p_form')
    return render(request, 'memocha/add_patient.html', {'form': form, 'formset': formset})


@login_required
def patient_details(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    # If the doctor tries to access the patient page of not
    # their patient, redirect to the doctor's dashboard
    if not request.user.doctor.patient_set.filter(pk=patient.pk):
        return redirect('/memocha/doctor')
    approval_videos = patient.videos_to_be_approved()
    approval_needed = [video.corresponding_dosage() for video in approval_videos]
    approval_needed_json = json.dumps(approval_needed, cls=DjangoJSONEncoder)
    if request.method == 'POST':
        # Remove the patient
        if request.POST.get('action', ) == 'remove':
            # Deleting the user will delete the patient
            patient.user.delete()
            # But we also need to delete any prescriptions
            # that are no longer related to anyone
            Prescription.objects.annotate(patients=Count('patient')).filter(patients=0).delete()
            return redirect('/memocha/doctor')
        elif 'approve' in request.POST:
            video = approval_videos[int(request.POST['approve'])]
            video.approved = True
            video.save()
        elif 'disapprove' in request.POST:
            video = approval_videos[int(request.POST['disapprove'])]
            video.approved = False
            video.save()
        else:  # Update Patient was clicked to update prescriptions
            # A set to keep track of which previously existing prescriptions
            # are in the new formset
            existing_prescriptions = set([prescription.pk for prescription in patient.prescriptions.all()])
            formset = formset_factory(PrescriptionForm)(request.POST, prefix='p_form')
            if formset.is_valid():
                for form in formset:
                    # Check to see if the form matches an existing prescription
                    matching_prescriptions = patient.prescriptions.filter(
                        medication=form.cleaned_data['medication'],
                        dosage=form.cleaned_data['dosage'],
                        dosage_times=form.cleaned_data['dosage_times']
                    )
                    if matching_prescriptions:
                        # Remove the matching prescription from the tracker
                        for prescription in matching_prescriptions:
                            existing_prescriptions.remove(prescription.pk)
                        # Don't need to add this one because it already exists
                        continue
                    # Add the new prescription.
                    prescription = form.save()
                    patient.prescriptions.add(prescription)
                # Any keys left in the existing_prescriptions set were not
                # present in the formset and we can assume they have been
                # removed
                for prescription in existing_prescriptions:
                    patient.prescriptions.remove(Prescription.objects.get(pk=prescription))
                # Delete any prescriptions that are no longer related to anyone
                Prescription.objects.annotate(patients=Count('patient')).filter(patients=0).delete()
                return redirect('/memocha/doctor')
    if patient.prescriptions.all():
        formset = modelformset_factory(Prescription, fields='__all__', extra=0)(prefix='p_form', queryset=patient.prescriptions.all())
    else:
        formset = modelformset_factory(Prescription, fields='__all__')(prefix='p_form')
    dates_of_interest = [(patient.user.date_joined + timedelta(days=i)).date()
                         for i in range(int((timezone.now() - patient.user.date_joined).days)+1)]
    video_list = []
    videos = patient.video_set.all()
    for video in videos:
        video_list.append(video.corresponding_dosage())
    video_list_json = json.dumps(video_list)
    prescriptions = list(patient.prescriptions.all().values_list())
    prescriptions_json = json.dumps(prescriptions, cls=DjangoJSONEncoder)
    return render(request, 'memocha/patient_details.html',
                  {
                      'patient': patient,
                      'formset': formset,
                      'dates_of_interest': [date.strftime('%d %b') for date in dates_of_interest],
                      'video_list': video_list_json,
                      'prescriptions': prescriptions_json,
                      'approval_needed': approval_needed_json,
                  })


@login_required
def record_video(request):

    if request.method == 'GET':
        return redirect('/memocha/patient')
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
    return render(request, 'memocha/record_video.html', {'form': form})
