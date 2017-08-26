from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import ArrayField


# The window of time on either side of the prescribed
# time a patient can record a dosage video.
# Units: seconds
DOSAGE_TIME_WIGGLE_ROOM = 1800


class Doctor(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)


class Prescription(models.Model):
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    dosage_times = ArrayField(models.TimeField())

    def __str__(self):
        time_string = ', '.join((time.strftime('%H:%M') for time in self.dosage_times))
        return '{0}: Take {1} at {2}'.format(
            self.medication,
            self.dosage,
            time_string
        )


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    prescriptions = models.ManyToManyField(Prescription, blank=True)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

    def recordable_medications(self):
        medications = []
        times = []
        now = timezone.localtime()
        already_recorded = self.videos_for_date(now.date())
        for prescription in self.prescriptions.all():
            for dosage_time in prescription.dosage_times:
                dosage_datetime = timezone.make_aware(datetime.combine(now.date(), dosage_time))
                time_dif = dosage_datetime - now
                if abs(time_dif.total_seconds()) <= DOSAGE_TIME_WIGGLE_ROOM:
                    # Check to see if the video has already been recorded
                    dosage_datetime = datetime.combine(now.date(), dosage_time)
                    start_time = dosage_datetime - timedelta(seconds=DOSAGE_TIME_WIGGLE_ROOM)
                    end_time = dosage_datetime + timedelta(seconds=DOSAGE_TIME_WIGGLE_ROOM)
                    if already_recorded.filter(
                        record_date__range=(start_time, end_time)
                    ).filter(
                        prescription=prescription
                    ):
                        continue
                    medications.append(prescription.medication)
                    times.append(dosage_time)
        return medications, times

    def next_medication(self):
        time_to_next_medication = timedelta(microseconds=-1)
        medications = []
        now = timezone.localtime()
        for prescription in self.prescriptions.all():
            for dosage_time in prescription.dosage_times:
                time_dif = timezone.make_aware(datetime.combine(now.date(), dosage_time)) - now
                time_dif_seconds = time_dif.total_seconds()

                next_medication_seconds = time_to_next_medication.total_seconds()
                if next_medication_seconds < 0:
                    # Haven't found a medication to take today yet
                    if time_dif_seconds >= 0:
                        # Found a medication to take today
                        time_to_next_medication = time_dif
                        medications = [prescription.medication, ]
                        break
                    else:
                        # Larger negative time_dif's means earlier in the day
                        if time_dif_seconds <= next_medication_seconds:
                            if time_dif_seconds == next_medication_seconds:
                                medications.append(prescription.medication)
                            else:
                                time_to_next_medication = time_dif
                                medications = [prescription.medication, ]
                else:
                    # There is at least one medication yet to be taken today
                    if time_dif_seconds < 0:
                        # Skip tomorrow's medications if we have one for today
                        continue
                    if time_dif_seconds <= next_medication_seconds:
                        if time_dif_seconds == next_medication_seconds:
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
        return self.video_set.filter(record_date__date=date)

    def videos_to_be_approved(self):
        """Gets the queryset of videos that still need to be approved."""
        return self.video_set.filter(approved=None)


class Video(models.Model):
    person = models.ForeignKey(Patient, on_delete=models.CASCADE)
    record_date = models.DateTimeField()
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    upload = models.FileField(upload_to='videos/')
    approved = models.NullBooleanField()

    def corresponding_dosage(self):
        localtime = timezone.localtime(self.record_date)
        record_hour = localtime.hour
        record_second = localtime.second
        possible_times = self.prescription.dosage_times
        timeslot = min(
            possible_times,
            key= lambda time: abs(
                (record_hour - time.hour) * 3600
                + (record_second - time.second)
            )
        )
        return {
            'medication': self.prescription.medication,
            'date': localtime.date().strftime('%d %b'),
            'timeslot': timeslot.strftime('%H:%M'),
            'url': self.upload.url,
            'approved': self.approved,
        }

    def __str__(self):
        return "{0} {1} {2} {3}".format(
            self.person.user.first_name,
            self.person.user.last_name,
            self.record_date,
            self.prescription.medication
        )
