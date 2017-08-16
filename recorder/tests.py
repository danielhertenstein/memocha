from django.test import TransactionTestCase
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
            person=Patient.objects.get(user__username='Patient'),
            record_date=current_datetime,
            prescription=prescription,
            upload=self.my_file,
        )

    def tearDown(self):
        Video.objects.get(pk=1).upload.delete()

    def test_date_and_time_details(self):
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
