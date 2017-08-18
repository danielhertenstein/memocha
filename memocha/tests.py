"""
In the interest of my own time, this is a subset
of the tests I would write for production code.
"""
from datetime import time, datetime
from freezegun import freeze_time

from django.test import TransactionTestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import make_password
from memocha.models import Doctor, Prescription, Patient, Video


class VideoTestCase(TransactionTestCase):
    def setUp(self):
        current_datetime = timezone.localtime()

        # Make the doctor and patient groups
        doctor_group = Group.objects.create(name='Doctors')
        patient_group = Group.objects.create(name='Patients')

        # Make a doctor
        doctor_user = User.objects.create_user(
            'Doctor',
            'doctor@example.com',
            'doctorpassword'
        )
        doctor_user.groups.add(doctor_group)
        doctor = Doctor.objects.create(
            user=doctor_user
        )

        # Make a patient
        patient_user = User.objects.create_user(
            'Patient',
            'patient@example.com',
            'patientpassword'
        )
        patient_user.groups.add(patient_group)
        patient = Patient.objects.create(
            user=patient_user,
            doctor=doctor,
            date_of_birth=current_datetime.date(),
        )

        # Make a prescription
        prescription = Prescription.objects.create(
            medication='test',
            dosage=1,
            dosage_times=[current_datetime,]
        )
        patient.prescriptions.add(prescription)

        # Make a video
        self.my_file = SimpleUploadedFile('test.txt', b'test contents')
        video = Video.objects.create(
            person=patient,
            record_date=current_datetime,
            prescription=prescription,
            upload=self.my_file,
        )

    def tearDown(self):
        Video.objects.get(pk=1).upload.delete()

    def test_date_and_time_details(self):
        """
        Tests that the right timeslot is returned for a test video.
        """
        prescription = Prescription.objects.get(medication='test')
        current_datetime = timezone.localtime()

        video = Video.objects.get(pk=1)

        expected_date = current_datetime.date().strftime('%d %b')
        expected_time = prescription.dosage_times[0].strftime('%H:%M')

        dosage = video.corresponding_dosage()
        self.assertEqual(dosage['medication'], 'test')
        self.assertEqual(dosage['date'], expected_date)
        self.assertEqual(dosage['timeslot'], expected_time)
        self.assertEqual(dosage['url'], '/media/videos/test.txt')
        self.assertEqual(dosage['approved'], None)


class PatientTestCase(TransactionTestCase):
    def setUp(self):
        current_datetime = timezone.localtime()

        # Make the doctor and patient groups
        doctor_group = Group.objects.create(name='Doctors')
        patient_group = Group.objects.create(name='Patients')

        # Make a doctor
        doctor_user = User.objects.create_user(
            'Doctor',
            'doctor@example.com',
            'doctorpassword'
        )
        doctor_user.groups.add(doctor_group)
        doctor = Doctor.objects.create(
            user=doctor_user
        )

        # Make a patient
        patient_user = User.objects.create_user(
            'Patient',
            'patient@example.com',
            'patientpassword'
        )
        patient_user.groups.add(patient_group)
        patient = Patient.objects.create(
            user=patient_user,
            doctor=doctor,
            date_of_birth=current_datetime.date(),
        )

        # Make two prescriptions
        prescription1 = Prescription.objects.create(
            medication='test',
            dosage=1,
            dosage_times=[
                time(hour=9),
                time(hour=12),
                time(hour=22),
            ]
        )
        prescription2 = Prescription.objects.create(
            medication='other_test',
            dosage=1,
            dosage_times=[
                time(hour=6),
                time(hour=11),
                time(hour=21),
            ]
        )
        patient.prescriptions.add(prescription1)
        patient.prescriptions.add(prescription2)


    def test_next_medication_at_end_of_day(self):
        """
        Tests the first medication of the day is returned when the method is
        called at the end of the day.
        """
        patient = Patient.objects.get(user__username='Patient')

        expected_prescription = Prescription.objects.get(medication='other_test')
        expected_name = [expected_prescription.medication, ]
        expected_time = expected_prescription.dosage_times[0]

        current_time = timezone.localtime()
        current_time = current_time.replace(hour=23, minute=0, second=0, microsecond=0)
        with freeze_time(current_time):
            medications, times = patient.next_medication()
            self.assertEqual(medications, expected_name)
            self.assertEqual(times, expected_time)

    def test_next_medication_in_middle_of_day(self):
        """
        Tests the first medication of the day is returned when the method is
        called in the middle of the day.
        """
        patient = Patient.objects.get(user__username='Patient')

        expected_prescription = Prescription.objects.get(medication='test')
        expected_name = [expected_prescription.medication, ]
        expected_time = expected_prescription.dosage_times[1]

        current_time = timezone.localtime()
        current_time = current_time.replace(hour=11, minute=30, second=0, microsecond=0)
        with freeze_time(current_time):
            medications, times = patient.next_medication()
            self.assertEqual(medications, expected_name)
            self.assertEqual(times, expected_time)


class HomeButtonTestCase(TransactionTestCase):
    """Tests the behavior of the home button"""

    def setUp(self):
        self.client = Client()

        # Make the doctor and patient groups
        doctor_group = Group.objects.create(name='Doctors')
        patient_group = Group.objects.create(name='Patients')

        # Make a doctor user
        doctor_user = User.objects.create_user(
            'Doctor',
            'doctor@example.com',
            'doctorpassword'
        )
        doctor_user.groups.add(doctor_group)
        doctor = Doctor.objects.create(
            user=doctor_user
        )

        # Make a patient user
        patient_user = User.objects.create_user(
            'Patient',
            'patient@example.com',
            'patientpassword'
        )
        patient_user.groups.add(patient_group)
        patient = Patient.objects.create(
            user=patient_user,
            doctor=doctor,
            date_of_birth=timezone.localtime().date(),
        )

    def test_not_logged_in(self):
        """Home button should take the vistor to the login screen."""
        response = self.client.get('/memocha/dashboard', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/login/?next=/memocha/dashboard/', status_code=301)
        self.assertTemplateUsed('accounts/login.html')
        self.assertEqual(response.resolver_match.view_name, 'django.contrib.auth.views.LoginView')

    def test_patient_pressed(self):
        """The logged in patient should be taken to the patient dashboard."""
        self.client.login(username='Patient', password='patientpassword')
        response = self.client.get('/memocha/dashboard', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/memocha/patient/', status_code=301)
        self.assertTemplateUsed('memocha/patient_dashboard.html')
        self.assertEqual(response.resolver_match.view_name, 'memocha:patient_dashboard')

    def test_doctor_pressed(self):
        """The logged in doctor should be taken to the doctor dashboard."""
        self.client.login(username='Doctor', password='doctorpassword')
        response = self.client.get('/memocha/dashboard', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/memocha/doctor/', status_code=301)
        self.assertTemplateUsed('memocha/doctor_dashboard.html')
        self.assertEqual(response.resolver_match.view_name, 'memocha:doctor_dashboard')


class PatientCreationTestCase(TransactionTestCase):
    """Tests form validation for the Patient Creation page."""

    def setUp(self):
        self.client = Client()

        # Make the doctor and patient groups
        doctor_group = Group.objects.create(name='Doctors')
        patient_group = Group.objects.create(name='Patients')

        # Make a doctor
        doctor_user = User.objects.create_user(
            'Doctor',
            'doctor@example.com',
            'doctorpassword'
        )
        doctor_user.groups.add(doctor_group)
        doctor = Doctor.objects.create(
            user=doctor_user
        )

        # Make a patient
        self.first_name = 'first'
        self.last_name = 'last'
        self.date_of_birth = datetime.now().date()
        self.secure_code = 'not_secure'
        self.email = 'patient@example.com'
        self.username='{0}_{1}_{2}'.format(
            self.first_name,
            self.last_name,
            self.date_of_birth
        )
        patient_user = User.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            password=make_password(self.secure_code),
            email=self.email
        )
        patient_user.groups.add(patient_group)
        patient = Patient.objects.create(
            user=patient_user,
            doctor=doctor,
            date_of_birth=self.date_of_birth,
        )

    def test_no_account_made_by_doctor(self):
        """
        Should inform patient that the doctor
        has not made an account for them yet.
        """
        form_data = {
            'first_name': 'different',
            'last_name': 'name',
            'email': 'fake@fake.com',
            'date_of_birth_day': '1',
            'date_of_birth_month': '1',
            'date_of_birth_year': '2017',
            'username': 'fake',
            'secure_code': '1234',
            'password1': 'new_password',
            'password2': 'new_password'
        }
        response = self.client.post(
            '/memocha/new_patient/',
            data=form_data,
            follow=True
        )
        expected_error = ('No matching patient record has been registered by a '
                          'doctor. Please check the name and date of birth '
                          'entered or contact your doctor to ensure your '
                          'record has been created.')
        self.assertFormError(response, 'form', None, expected_error)

    def test_account_already_made(self):
        """Should inform patient that their account is already activated."""
        # If the account is already activated, the user should exist, but the
        # username and password should have changed from the default.
        patient = Patient.objects.get(user__username=self.username)
        patient.user.username = 'updated_username'
        patient.user.set_password('updated_password')
        patient.user.save()

        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'date_of_birth_day': self.date_of_birth.day,
            'date_of_birth_month': self.date_of_birth.month,
            'date_of_birth_year': self.date_of_birth.year,
            'username': 'new_username',
            'secure_code': self.secure_code,
            'password1': 'new_password',
            'password2': 'new_password'
        }
        response = self.client.post(
            '/memocha/new_patient/',
            data=form_data,
            follow=True
        )
        expected_error = ('An account with this name and date of birth has '
                          'already been activated. Return to the home screen '
                          'and log in.')
        self.assertFormError(response, 'form', None, expected_error)

    def test_first_name_mismatch(self):
        """
        Should inform patient that their personal information
        does not match that provided by the doctor.
        """
        form_data = {
            'first_name': 'wrong',
            'last_name': self.last_name,
            'email': self.email,
            'date_of_birth_day': self.date_of_birth.day,
            'date_of_birth_month': self.date_of_birth.month,
            'date_of_birth_year': self.date_of_birth.year,
            'username': 'new_username',
            'secure_code': self.secure_code,
            'password1': 'new_password',
            'password2': 'new_password'
        }
        response = self.client.post(
            '/memocha/new_patient/',
            data=form_data,
            follow=True
        )
        expected_error = ('No matching patient record has been registered by a '
                          'doctor. Please check the name and date of birth '
                          'entered or contact your doctor to ensure your '
                          'record has been created.')
        self.assertFormError(response, 'form', None, expected_error)

    def test_last_name_mismatch(self):
        """
        Should inform patient that their personal information
        does not match that provided by the doctor.
        """
        form_data = {
            'first_name': self.first_name,
            'last_name': 'wrong',
            'email': self.email,
            'date_of_birth_day': self.date_of_birth.day,
            'date_of_birth_month': self.date_of_birth.month,
            'date_of_birth_year': self.date_of_birth.year,
            'username': 'new_username',
            'secure_code': self.secure_code,
            'password1': 'new_password',
            'password2': 'new_password'
        }
        response = self.client.post(
            '/memocha/new_patient/',
            data=form_data,
            follow=True
        )
        expected_error = ('No matching patient record has been registered by a '
                          'doctor. Please check the name and date of birth '
                          'entered or contact your doctor to ensure your '
                          'record has been created.')
        self.assertFormError(response, 'form', None, expected_error)

    def test_date_of_birth_mismatch(self):
        """
        Should inform patient that their personal information
        does not match that provided by the doctor.
        """
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'date_of_birth_day': self.date_of_birth.day,
            'date_of_birth_month': self.date_of_birth.month,
            'date_of_birth_year': self.date_of_birth.year - 1,
            'username': 'new_username',
            'secure_code': self.secure_code,
            'password1': 'new_password',
            'password2': 'new_password'
        }
        response = self.client.post(
            '/memocha/new_patient/',
            data=form_data,
            follow=True
        )
        expected_error = ('No matching patient record has been registered by a '
                          'doctor. Please check the name and date of birth '
                          'entered or contact your doctor to ensure your '
                          'record has been created.')
        self.assertFormError(response, 'form', None, expected_error)

    def test_secure_code_mismatch(self):
        """
        Should inform patient that their personal information
        does not match that provided by the doctor.
        """
        form_data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'date_of_birth_day': self.date_of_birth.day,
            'date_of_birth_month': self.date_of_birth.month,
            'date_of_birth_year': self.date_of_birth.year,
            'username': 'new_username',
            'secure_code': 'wrong',
            'password1': 'new_password',
            'password2': 'new_password'
        }
        response = self.client.post(
            '/memocha/new_patient/',
            data=form_data,
            follow=True
        )
        expected_error = ('The secure code entered do not match that provided '
                          'by your doctor. Please try again.')
        self.assertFormError(response, 'form', None, expected_error)
