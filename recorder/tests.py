"""
In the interest of my own time, this is a subset
of the tests I would write for production code.
"""
from datetime import time
from freezegun import freeze_time

from django.test import TransactionTestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from recorder.models import Doctor, Prescription, Patient, Video


class VideoTestCase(TransactionTestCase):
    def setUp(self):
        current_datetime = timezone.now()

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
        current_datetime = timezone.now()

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
        current_datetime = timezone.now()

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

        current_time = timezone.now()
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

        current_time = timezone.now()
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
            date_of_birth=timezone.now().date(),
        )

    def test_not_logged_in(self):
        """Home button should take the vistor to the login screen."""
        response = self.client.get('/recorder/dashboard', follow=True)
        # TODO: Check the redirect goes to the right place.
        # TODO: Check the status code?
        # TODO: Check the correct template has been loaded.
        #self.assertRedirects()
        print('boo')

    def test_patient_pressed(self):
        """The logged in patient should be taken to the patient dashboard."""
        self.client.login(username='Patient', password='patientpassword')
        response = self.client.get('/recorder/dashboard', follow=True)
        # TODO: Check the redirect goes to the right place.
        # TODO: Check the status code?
        # TODO: Check the correct template has been loaded.
        #self.assertRedirects()
        print('boo')

    def test_doctor_pressed(self):
        """The logged in doctor should be taken to the doctor dashboard."""
        self.client.login(username='Doctor', password='doctorpassword')
        response = self.client.get('/recorder/dashboard', follow=True)
        # TODO: Check the redirect goes to the right place.
        # TODO: Check the status code?
        # TODO: Check the correct template has been loaded.
        #self.assertRedirects()
        print('boo')
