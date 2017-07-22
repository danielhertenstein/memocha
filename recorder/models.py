from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField


# The window of time around the prescribed
# time a patient can record a dosage video.
# Units: seconds
DOSAGE_TIME_WIGGLE_ROOM = 36000


class Doctor(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)


class Prescription(models.Model):
    medication = models.CharField(max_length=100)
    dosage = models.IntegerField()
    dosage_times = ArrayField(models.TimeField())

    def __str__(self):
        time_string = ', '.join((time.strftime('%H:%M') for time in self.dosage_times))
        return '{0}: Take {1} at {2}'.format(
            self.medication,
            self.dosage,
            time_string
        )


class Patient(models.Model):
    user = models.OneToOneField(User)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    prescriptions = models.ManyToManyField(Prescription, blank=True)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

    def recordable_medications(self):
        from datetime import datetime
        medications = []
        times = []
        now = datetime.now()
        for prescription in self.prescriptions.all():
            for dosage_time in prescription.dosage_times:
                time_dif = (dosage_time.hour - now.hour) * 3600 + (dosage_time.second - now.second)
                if abs(time_dif) <= DOSAGE_TIME_WIGGLE_ROOM:
                    medications.append(prescription.medication)
                    times.append(dosage_time)
        return medications, times

    def next_medication(self):
        from datetime import datetime, date, timedelta
        time_to_next_medication = timedelta(days=2)
        medications = []
        now = datetime.now()
        for prescription in self.prescriptions.all():
            for dosage_time in prescription.dosage_times:
                time_dif = datetime.combine(date.today(), dosage_time) - now
                if (time_dif.seconds > 0) and (time_dif <= time_to_next_medication):
                    if time_dif == time_to_next_medication:
                        medications.append(prescription.medication)
                    else:
                        time_to_next_medication = time_dif
                        medications = [prescription.medication, ]
                    break
        time_of_next_medication = (now + time_to_next_medication).time()
        return medications, time_of_next_medication

    def videos_for_date(self, date):
        """For a given date, return the videos recorded for the patient's
        prescriptions.

        :param date: The date to get videos for.
        :return: Not sure yet.
        """


class Video(models.Model):
    person = models.ForeignKey(Patient, on_delete=models.CASCADE)
    record_date = models.DateTimeField()
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    # TODO: Hook this up correctly.
    upload = models.FileField(upload_to='videos/')

    def __str__(self):
        return "{0} {1} {2} {3}".format(
            self.person.user.first_name,
            self.person.user.last_name,
            self.record_date,
            self.prescription.medication
        )
