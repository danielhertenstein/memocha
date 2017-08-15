from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Group
from recorder.models import Doctor, Prescription, Patient, Video


class VideoTestCase(TestCase):
    def setUp(self):
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
        # TODO: Finish making doctor and change patient's doctor from the user.
        # Make a patient
        patient_user = User.objects.create_user(
            'Patient',
            'patient@example.com',
            'patientpassword'
        )
        patient_user.groups.add(patient_group)
        patient = Patient.objects.create(
            user=patient_user,
            doctor=doctor_user,
            date_of_birth=timezone.now().date(),
        )
        # Make a prescription
        prescription = Prescription.objects.create(
            medication='test',
            dosage=1,
            dosage_times=[timezone.now(),]
        )
        patient.prescriptions.add(prescription)

    def test_setup(self):
        print('boo')
