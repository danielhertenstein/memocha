from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Doctor(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)


class Prescription(models.Model):
    medication = models.CharField(max_length=100)
    dosage = models.IntegerField()
    dosage_times = ArrayField(models.TimeField())

    def __str__(self):
        # TODO: Revisit when format is setup
        return self.medication


class Patient(models.Model):
    user = models.OneToOneField(User)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    prescriptions = models.ManyToManyField(Prescription, blank=True)

    def __str__(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)


class Video(models.Model):
    person = models.ForeignKey(Patient, on_delete=models.CASCADE)
    record_date = models.DateTimeField()
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    # TODO: Hook this up correctly.
    upload = models.FileField()

    def __str__(self):
        return "{0} {1} {2} {3}".format(
            self.person.user.first_name,
            self.person.user.last_name,
            self.record_date,
            self.prescription.medication
        )
